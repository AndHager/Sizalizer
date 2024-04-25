#include "llvm/IR/CFG.h"
#include "llvm/IR/PassManager.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/CodeGen/MachineFunction.h"

#include <iostream>
#include <mgclient.h>

using namespace llvm;
using namespace std;

#define DEBUG false

#define PRINT_IR false
#define PURGE_DB false

namespace
{

    struct CDFGPass : public PassInfoMixin<CDFGPass>
    {
        string get_bb_name(BasicBlock *bb)
        {
            string str;
            raw_string_ostream OS(str);
            bb->printAsOperand(OS, false);
            return OS.str();
        }

        template <typename LLVM_Type>
        string llvm_to_string(LLVM_Type *obj)
        {
            string str;
            raw_string_ostream OS(str);
            OS << *obj << "\n";
            return OS.str();
        }

        mg_session *connect_to_db(const char *host, uint16_t port)
        {
            mg_init();
#if DEBUG
            printf("mgclient version: %s\n", mg_client_version());
#endif

            mg_session_params *params = mg_session_params_make();
            if (!params)
            {
                fprintf(stderr, "failed to allocate session parameters\n");
                exit(1);
            }
            mg_session_params_set_host(params, host);
            mg_session_params_set_port(params, port);
            mg_session_params_set_sslmode(params, MG_SSLMODE_DISABLE);

            mg_session *session = NULL;
            int status = mg_connect(params, &session);
            mg_session_params_destroy(params);
            if (status < 0)
            {
                printf("failed to connect to Memgraph: %s\n", mg_session_error(session));
                mg_session_destroy(session);
                exit(1);
            }
            return session;
        }

        void disconnect(mg_session *session)
        {
            mg_session_destroy(session);
            mg_finalize();
        }

        void exec_qeury(mg_session *session, const char *query)
        {
            if (mg_session_run(session, query, NULL, NULL, NULL, NULL) < 0)
            {
                outs() << "failed to execute query: " << query << " mg error: " << mg_session_error(session) << "\n";
                mg_session_destroy(session);
                exit(1);
            }
            if (mg_session_pull(session, NULL))
            {
                outs() << "failed to pull results of the query: " << mg_session_error(session) << "\n";
                mg_session_destroy(session);
                exit(1);
            }

            int status = 0;
            mg_result *result;
            int rows = 0;
            while ((status = mg_session_fetch(session, &result)) == 1)
            {
                rows++;
            }

            if (status < 0)
            {
                outs() << "error occurred during query execution: " << mg_session_error(session) << "\n";
            }
            else
            {
#if DEBUG
                printf("query executed successfuly and returned %d rows\n", rows);
#endif
            }
        }

        void connect_bbs(mg_session *session, BasicBlock *first_bb, BasicBlock *second_bb, string f_name, string module_name)
        {
            // MERGE: create if not exist else match
            string store_first = "MERGE (first_bb {name: '" + get_bb_name(first_bb) + "', func_name: '" + f_name + "', module_name: '" + module_name + "'})";
            string set_frist_code = " SET first_bb.code =  '" + sanitize_str(llvm_to_string(first_bb)) + "'";
            string store_second = " MERGE (second_bb {name: '" + get_bb_name(second_bb) + "', func_name: '" + f_name + "', module_name: '" + module_name + "'})";
            string set_second_code = " SET second_bb.code =  '" + sanitize_str(llvm_to_string(second_bb)) + "'";
            string rel = " MERGE (first_bb)-[:CFG]->(second_bb);";
            string qry = store_first + set_frist_code + store_second + set_second_code + rel;
            exec_qeury(session, qry.c_str());
        }

        string sanitize_str(string str) {
            const string illegal_chars = "\n\"\\\'\t()[]{}~";
            for (char c : illegal_chars) { 
                replace(str.begin(), str.end(), c, '_');
            }
            return str;
        }

        void connect_insts(mg_session *session, string src_str, string src_op_name, string dst_str, string dst_op_name, string f_name, string module_name)
        {
            // MERGE: create if not exist else match
            src_str = sanitize_str(src_str);
            dst_str = sanitize_str(dst_str);

            string store_src = "MERGE (src_inst {name: '" + src_op_name + "', inst: '" + src_str + "', func_name: '" + f_name + "', module_name: '" + module_name + "'})";
            string store_dst = "MERGE (dst_inst {name: '" + dst_op_name + "', inst: '" + dst_str + "', func_name: '" + f_name + "', module_name: '" + module_name + "'})";
            string rel = "MERGE (src_inst)-[:DFG]->(dst_inst);";
            string qry = store_src + '\n' + store_dst + '\n' + rel + '\n';
            exec_qeury(session, qry.c_str());
        }

        PreservedAnalyses run(Module &M, ModuleAnalysisManager &MAM)
        {
#if DEBUG
            outs() << "Running CDFGPass\n";
#endif
            mg_session *session = connect_to_db("localhost", 7687);

#if PURGE_DB
            // Clear database
            auto del = "MATCH (n) DETACH DELETE n;";
            exec_qeury(session, del);
#endif

            // Push CDFG to DB
            string module_name = M.getName().str();
#if PRINT_IR
            outs() << "Module Name: " << module_name << "\n";
#endif
            for (Function &F : M)
            {
                string f_name = F.getName().str();
#if PRINT_IR
                outs() << " Function: " << f_name << "\n";
#endif
                for (BasicBlock &bb : F)
                {
                    string bb_name = get_bb_name(&bb);
#if PRINT_IR
                    outs() << "  Label: " << bb_name << "\n";
#endif
                    for (BasicBlock *suc_bb : successors(&bb))
                    {
                        connect_bbs(session, &bb, suc_bb, f_name, module_name);
                    }

                    for (Instruction &inst : bb)
                    {
                        string inst_str = llvm_to_string(&inst);
                        string op_name = inst.getOpcodeName();
#if PRINT_IR
                        outs() << "   " << inst_str;
#endif

                        Instruction::op_iterator opEnd = inst.op_end();
                        for (Instruction::op_iterator opi = inst.op_begin(); opi != opEnd; opi++)
                        {

                            Value *op = opi->get();
                            Type *tp = op->getType();
                            if (!tp->isLabelTy())
                            {
                                string src_str = llvm_to_string(op);
                                string src_op_name = "Const";
                                
                                Instruction *src_inst = dyn_cast<Instruction>(op);
                                if (src_inst) {
                                    src_op_name = src_inst->getOpcodeName();
                                }
#if DEBUG
                                outs() << "    - " << src_str;
#endif
                                connect_insts(session, src_str, src_op_name, inst_str, op_name, f_name, module_name);
                            }
                        }
                    }
                }
            }

            disconnect(session);

            return PreservedAnalyses::all();
        }
    };

} // end anonymous namespace

PassPluginLibraryInfo
getPassPluginInfo()
{
    const auto callback = [](PassBuilder &PB)
    {
        PB.registerOptimizerLastEPCallback(
            [&](ModulePassManager &MPM, auto)
            {
                MPM.addPass(CDFGPass());
                return true;
            });
    };

    return {LLVM_PLUGIN_API_VERSION, "name", "0.0.1", callback};
};

extern "C" LLVM_ATTRIBUTE_WEAK PassPluginLibraryInfo llvmGetPassPluginInfo()
{
    return getPassPluginInfo();
}
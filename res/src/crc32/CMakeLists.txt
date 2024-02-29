file(GLOB SOURCES *.c)
file(GLOB HEADERS *.h)
add_executable_etiss(crc32 ${SOURCES} ${HEADERS})

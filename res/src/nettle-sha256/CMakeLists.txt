file(GLOB SOURCES *.c)
file(GLOB HEADERS *.h)
add_executable_etiss(nettle-sha256 ${SOURCES} ${HEADERS})

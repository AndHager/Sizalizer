file(GLOB SOURCES *.c)
file(GLOB HEADERS *.h)
add_executable_etiss(slre ${SOURCES} ${HEADERS})

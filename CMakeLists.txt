cmake_minimum_required(VERSION 3.13)
project(pwatch)

add_subdirectory(thirdparty)
add_subdirectory(src)
install(TARGETS pwatch LIBRARY DESTINATION pwatch)
install(TARGETS test_helper RUNTIME DESTINATION pwatch/tests)

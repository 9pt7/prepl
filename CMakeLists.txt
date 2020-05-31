cmake_minimum_required(VERSION 3.13)
project(prepl VERSION 0.0.0)

add_subdirectory(thirdparty)
add_subdirectory(src)
install(TARGETS prepl LIBRARY DESTINATION prepl)
install(TARGETS test_helper RUNTIME DESTINATION prepl/tests)

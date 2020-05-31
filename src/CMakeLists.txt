add_library(prepl SHARED prepl.cc)
target_compile_features(prepl PUBLIC cxx_std_17)
target_link_libraries(prepl dl nlohmann_json stdc++fs)
add_custom_command(TARGET prepl POST_BUILD
  COMMAND ${CMAKE_COMMAND} -E copy_if_different
  $<TARGET_FILE:prepl>
  ${PROJECT_SOURCE_DIR}/prepl
  )

add_executable(test_helper test_helper.cc)
target_compile_features(test_helper PUBLIC cxx_std_17)
target_link_libraries(test_helper nlohmann_json)
add_custom_command(TARGET test_helper POST_BUILD
  COMMAND ${CMAKE_COMMAND} -E copy_if_different
  $<TARGET_FILE:test_helper>
  ${PROJECT_SOURCE_DIR}/prepl/tests
  )

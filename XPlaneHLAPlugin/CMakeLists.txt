#########################################################################
# CMakeLists.txt for the XPlane project
#########################################################################
PROJECT(XPlaneHLAPlugin CXX)

#########################################################################
# Setup reasonable default CMake behavior
#########################################################################

# CERTI requires CMake 2.4.x
CMAKE_MINIMUM_REQUIRED(VERSION 2.4.4)

# Detect the CERTI installation, http://www.cert.fr/CERTI
IF ("$ENV{CERTI_HOME}" STRGREATER "")
    # note: the CERTI_PATH_HOME is used to install the .fed file
    FILE(TO_CMAKE_PATH "$ENV{CERTI_HOME}" CERTI_PATH_HOME)
    LIST(APPEND CMAKE_MODULE_PATH ${CERTI_PATH_HOME}/share/scripts)
ENDIF()

# You should uncomment the following line if you want VERBOSE build
#SET(CMAKE_VERBOSE_MAKEFILE ON)

# The preferred (default) behaviour is to build library as shared on all platform
OPTION(BUILD_SHARED
  "Build libraries as shared library" ON)
IF (BUILD_SHARED)
  SET(BUILD_SHARED_LIBS ON)
ELSE (BUILD_SHARED)
  SET(BUILD_SHARED_LIBS OFF)
ENDIF (BUILD_SHARED)

# Change the build type to release when you are ready to release 
SET(CMAKE_BUILD_TYPE "Debug")
SET(EXECUTABLE_OUTPUT_PATH ${PROJECT_BINARY_DIR}/bin)
SET(LIBRARY_OUTPUT_PATH ${PROJECT_BINARY_DIR}/bin)

#SET(CMAKE_BUILD_TYPE "Release")

#########################################################################
# Define your project packaging basics
#########################################################################
SET(PACKAGE_NAME      ${CMAKE_PROJECT_NAME})
SET(PACKAGE_VERSION_MAJOR "0")
SET(PACKAGE_VERSION_MINOR "3")
SET(PACKAGE_VERSION_PATCH "0")
SET(PACKAGE_VERSION   "${PACKAGE_VERSION_MAJOR}.${PACKAGE_VERSION_MINOR}.${PACKAGE_VERSION_PATCH}")
SET(PACKAGE_BUGREPORT "jean-michel.mathe@onecert.fr")
MESSAGE(STATUS "Configuring ${PACKAGE_NAME} version ${PACKAGE_VERSION}")

#########################################################################
# Call i.e. INCLUDE the HLA RTI usage configuration
#########################################################################
CMAKE_MINIMUM_REQUIRED(VERSION 2.6.3)
# The FindRTI.cmake module is available since cmake 2.6.3
FIND_PACKAGE(RTI REQUIRED)
INCLUDE_DIRECTORIES(${RTI_INCLUDE_DIR})
ADD_DEFINITIONS(${RTI_DEFINITIONS})

#########################################################################
# CPack specific Configuration
#########################################################################
SET(CPACK_PACKAGE_DESCRIPTION_SUMMARY "XPlane Federation using M&S HLA")
SET(CPACK_PACKAGE_VENDOR "ONERA, CT/TIS, JMMath�")
SET(CPACK_PACKAGE_DESCRIPTION_FILE "${CMAKE_CURRENT_SOURCE_DIR}/XPlane_DESCRIPTION.txt")
SET(CPACK_RESOURCE_FILE_LICENSE "${CMAKE_CURRENT_SOURCE_DIR}/COPYING")
SET(CPACK_PACKAGE_NAME ${CMAKE_PROJECT_NAME})
SET(CPACK_SYSTEM_NAME ${CMAKE_SYSTEM_NAME})
SET(CPACK_SOURCE_IGNORE_FILES "/CVS/;/\\\\.svn/;\\\\.swp$;\\\\.#;/#;.*~;cscope.*")
SET(CPACK_SOURCE_GENERATOR "ZIP;TGZ")
IF (WIN32)
  SET(CPACK_GENERATOR "ZIP;NSIS")
  ## Add a custom target callable from IDE (Mostly for Visual Studio)
  GET_FILENAME_COMPONENT(CPACK_COMMAND ${CMAKE_COMMAND} PATH)
  SET(CPACK_COMMAND ${CPACK_COMMAND}/cpack)
  ADD_CUSTOM_TARGET(PACKAGE_SOURCE_ZIP
              COMMAND ${CPACK_COMMAND} -G ZIP --config CPackSourceConfig.cmake
              COMMENTS "Build a ZIP file containing the source")              
  # NSIS installer specific part
  INCLUDE(InstallRequiredSystemLibraries)
ELSE (WIN32)
  SET(CPACK_GENERATOR "ZIP;TGZ")
ENDIF(WIN32)
SET(CPACK_PACKAGE_VERSION ${PACKAGE_VERSION})
SET(CPACK_PACKAGE_VERSION_MAJOR ${PACKAGE_VERSION_MAJOR})
SET(CPACK_PACKAGE_VERSION_MINOR ${PACKAGE_VERSION_MINOR})
SET(CPACK_PACKAGE_VERSION_PATCH ${PACKAGE_VERSION_PATCH})

INCLUDE(CPack)

LIST(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}")
FIND_PACKAGE(XPlane)
INCLUDE_DIRECTORIES(XPlane_Common ${XPLANE_XPLM_INCLUDE_DIR} ${XPLANE_XPW_INCLUDE_DIR})

FIND_PACKAGE(PhiDget)
IF (PHIDGET_FOUND)
   ADD_SUBDIRECTORY(XPlane_PhiDget)
ENDIF(PHIDGET_FOUND)
ADD_SUBDIRECTORY(XPlane_Cde)
ADD_SUBDIRECTORY(XPlane_Out)
ADD_SUBDIRECTORY(XPlane_Trace)
ADD_SUBDIRECTORY(initFile)

MESSAGE(STATUS "*** ${CMAKE_PROJECT_NAME} has been successfully configured ***")

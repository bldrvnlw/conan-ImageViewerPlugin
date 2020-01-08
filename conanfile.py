from conans import ConanFile, CMake, tools
import os
import shutil
import json

class ImageViewerPluginConan(ConanFile):
    #TODO wrap with Conan build tools to extract version from source
    name = "ImageViewerPlugin"
    version = "0.1.0"
    license = "MIT"
    author = "B. van Lew b.van_lew@lumc.nl"
    # The url for the conan recipe
    url = "https://github.com/bldrvnlw/conan-ImageViewerPlugin"
    description = "A plugin for viewing image data in the high-dimensional plugin system (HDPS)."
    topics = ("hdps", "plugin", "image data", "loading")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    exports_sources = ["CMakeLists.txt", "build_trigger.json"]
    generators = "cmake"

    # Custom attributes for Bincrafters recipe conventions
    _source_subfolder = name
    _build_subfolder = "build_subfolder"
    install_dir = None
    
    requires = (
        "qt/5.12.4@lkeb/stable", 
        "hdps-core/0.1.0@lkeb/stable"
    )

    # Make a login url to pull the source 
    access_token = os.environ["CONAN_BLDRVNLW_TOKEN"]
    validated_url = "https://{0}:{1}@github.com/hdps/{2}".format("bldrvnlw", access_token, name)

    def _get_commit_sha(self, file_name):
        commit_sha = ""
        with open(file_name) as json_f:
            commit_info = json.load(json_f)
            commit_sha = commit_info["head_commit"]["id"]
        return commit_sha 
        
    def source(self):
        arr = os.listdir()
        print('Files: ', arr)
        commit_sha = self._get_commit_sha("build_trigger.json")
        self.run("git clone {0}.git".format(self.validated_url))
        os.chdir("./{0}".format(self._source_subfolder))
        self.run("git checkout {0}".format(commit_sha))
        
        # This small hack might be useful to guarantee proper /MT /MD linkage
        # in MSVC if the packaged project doesn't have variables to set it
        # properly
        conanproj = ("PROJECT(${PROJECT})\n"
                "include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)\n"
                "conan_basic_setup()\n"
        )
        os.chdir("..")
        tools.replace_in_file("ImageViewerPlugin/CMakeLists.txt", "PROJECT(${PROJECT})", conanproj)

    def _configure_cmake(self):
        cmake = CMake(self)
        if self.settings.os == "Windows" and self.options.shared:
            cmake.definitions["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True            
        cmake.configure(source_folder="ImageViewerPlugin")
        cmake.verbose = True
        return cmake
        
    def build(self):
        # If the user has no preference in HDPS_INSTALL_DIR simply set the install dir
        if not os.environ.get('HDPS_INSTALL_DIR', None):
            os.environ['HDPS_INSTALL_DIR'] = os.path.join(self.build_folder, "install")
        print('HDPS_INSTALL_DIR: ', os.environ['HDPS_INSTALL_DIR']) 
        self.install_dir = os.environ['HDPS_INSTALL_DIR'] 
        
        # The ImageViewerPlugin build expects the HDPS package to be in this install dir
        hdps_pkg_root= self.deps_cpp_info["hdps-core"].rootpath 
        print("Install dir type: ", os.path.join(self.install_dir, self.settings.get_safe("build_type")))
        shutil.copytree(hdps_pkg_root, os.path.join(self.install_dir, self.settings.get_safe("build_type"))) 
        
        cmake = self._configure_cmake()
        cmake.build() 


    def package(self):
        self.copy("*.h", dst="include", keep_path=False)
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["ImageViewerPlugin"]


#!/usr/bin/env python3
"""Generate a deterministic ESP32Monitor.xcodeproj/project.pbxproj.

Classic (explicit) pbxproj format, objectVersion 56 (Xcode 14+).
Every object ID is derived from a stable name via MD5 so references match.
"""
import hashlib
import os

PROJ_DIR = os.path.dirname(os.path.abspath(__file__))
APP = "ESP32Monitor"
BUNDLE_ID = "com.espectre.ESP32Monitor"
SWIFT_FILES = [
    "ESP32MonitorApp.swift",
    "Config.swift",
    "Models.swift",
    "RoomStatus.swift",
    "APIClient.swift",
    "LocationViewModel.swift",
    "RoomCardView.swift",
    "LocationView.swift",
    "FloorPlanModels.swift",
    "FloorPlanAPI.swift",
    "FloorPlanViewModel.swift",
    "FloorPlanView.swift",
    "RoomScanView.swift",
]
INFO_PLIST = "Info.plist"


def oid(key: str) -> str:
    """Deterministic 24-char uppercase hex ID."""
    return hashlib.md5(key.encode()).hexdigest()[:24].upper()


def main():
    # IDs
    proj = oid("project")
    target = oid("target")
    product = oid("product.app")
    main_group = oid("group.main")
    src_group = oid("group.src")
    products_group = oid("group.products")
    src_phase = oid("phase.sources")
    frameworks_phase = oid("phase.frameworks")
    resources_phase = oid("phase.resources")
    proj_cfg_list = oid("cfglist.project")
    target_cfg_list = oid("cfglist.target")
    proj_debug = oid("cfg.project.debug")
    proj_release = oid("cfg.project.release")
    target_debug = oid("cfg.target.debug")
    target_release = oid("cfg.target.release")

    file_refs = {f: oid("fileref." + f) for f in SWIFT_FILES + [INFO_PLIST]}
    build_files = {f: oid("buildfile." + f) for f in SWIFT_FILES}

    L = []
    L.append("// !$*UTF8*$!")
    L.append("{")
    L.append("\tarchiveVersion = 1;")
    L.append("\tclasses = {")
    L.append("\t};")
    L.append("\tobjectVersion = 56;")
    L.append("\tobjects = {")

    # PBXBuildFile
    L.append("")
    L.append("/* Begin PBXBuildFile section */")
    for f in SWIFT_FILES:
        L.append(f"\t\t{build_files[f]} /* {f} in Sources */ = "
                 f"{{isa = PBXBuildFile; fileRef = {file_refs[f]} /* {f} */; }};")
    L.append("/* End PBXBuildFile section */")

    # PBXFileReference
    L.append("")
    L.append("/* Begin PBXFileReference section */")
    L.append(f"\t\t{product} /* {APP}.app */ = {{isa = PBXFileReference; "
             f"explicitFileType = wrapper.application; includeInIndex = 0; "
             f"path = {APP}.app; sourceTree = BUILT_PRODUCTS_DIR; }};")
    for f in SWIFT_FILES:
        L.append(f"\t\t{file_refs[f]} /* {f} */ = {{isa = PBXFileReference; "
                 f"lastKnownFileType = sourcecode.swift; path = {f}; "
                 f"sourceTree = \"<group>\"; }};")
    L.append(f"\t\t{file_refs[INFO_PLIST]} /* {INFO_PLIST} */ = {{isa = PBXFileReference; "
             f"lastKnownFileType = text.plist.xml; path = {INFO_PLIST}; "
             f"sourceTree = \"<group>\"; }};")
    L.append("/* End PBXFileReference section */")

    # PBXFrameworksBuildPhase
    L.append("")
    L.append("/* Begin PBXFrameworksBuildPhase section */")
    L.append(f"\t\t{frameworks_phase} /* Frameworks */ = {{")
    L.append("\t\t\tisa = PBXFrameworksBuildPhase;")
    L.append("\t\t\tbuildActionMask = 2147483647;")
    L.append("\t\t\tfiles = (")
    L.append("\t\t\t);")
    L.append("\t\t\trunOnlyForDeploymentPostprocessing = 0;")
    L.append("\t\t};")
    L.append("/* End PBXFrameworksBuildPhase section */")

    # PBXGroup
    L.append("")
    L.append("/* Begin PBXGroup section */")
    # main group
    L.append(f"\t\t{main_group} = {{")
    L.append("\t\t\tisa = PBXGroup;")
    L.append("\t\t\tchildren = (")
    L.append(f"\t\t\t\t{src_group} /* {APP} */,")
    L.append(f"\t\t\t\t{products_group} /* Products */,")
    L.append("\t\t\t);")
    L.append("\t\t\tsourceTree = \"<group>\";")
    L.append("\t\t};")
    # source group
    L.append(f"\t\t{src_group} /* {APP} */ = {{")
    L.append("\t\t\tisa = PBXGroup;")
    L.append("\t\t\tchildren = (")
    for f in SWIFT_FILES:
        L.append(f"\t\t\t\t{file_refs[f]} /* {f} */,")
    L.append(f"\t\t\t\t{file_refs[INFO_PLIST]} /* {INFO_PLIST} */,")
    L.append("\t\t\t);")
    L.append(f"\t\t\tpath = {APP};")
    L.append("\t\t\tsourceTree = \"<group>\";")
    L.append("\t\t};")
    # products group
    L.append(f"\t\t{products_group} /* Products */ = {{")
    L.append("\t\t\tisa = PBXGroup;")
    L.append("\t\t\tchildren = (")
    L.append(f"\t\t\t\t{product} /* {APP}.app */,")
    L.append("\t\t\t);")
    L.append("\t\t\tname = Products;")
    L.append("\t\t\tsourceTree = \"<group>\";")
    L.append("\t\t};")
    L.append("/* End PBXGroup section */")

    # PBXNativeTarget
    L.append("")
    L.append("/* Begin PBXNativeTarget section */")
    L.append(f"\t\t{target} /* {APP} */ = {{")
    L.append("\t\t\tisa = PBXNativeTarget;")
    L.append(f"\t\t\tbuildConfigurationList = {target_cfg_list} /* Build configuration list for PBXNativeTarget \"{APP}\" */;")
    L.append("\t\t\tbuildPhases = (")
    L.append(f"\t\t\t\t{src_phase} /* Sources */,")
    L.append(f"\t\t\t\t{frameworks_phase} /* Frameworks */,")
    L.append(f"\t\t\t\t{resources_phase} /* Resources */,")
    L.append("\t\t\t);")
    L.append("\t\t\tbuildRules = (")
    L.append("\t\t\t);")
    L.append("\t\t\tdependencies = (")
    L.append("\t\t\t);")
    L.append(f"\t\t\tname = {APP};")
    L.append(f"\t\t\tproductName = {APP};")
    L.append(f"\t\t\tproductReference = {product} /* {APP}.app */;")
    L.append("\t\t\tproductType = \"com.apple.product-type.application\";")
    L.append("\t\t};")
    L.append("/* End PBXNativeTarget section */")

    # PBXProject
    L.append("")
    L.append("/* Begin PBXProject section */")
    L.append(f"\t\t{proj} /* Project object */ = {{")
    L.append("\t\t\tisa = PBXProject;")
    L.append("\t\t\tattributes = {")
    L.append("\t\t\t\tBuildIndependentTargetsInParallel = 1;")
    L.append("\t\t\t\tLastSwiftUpdateCheck = 1500;")
    L.append("\t\t\t\tLastUpgradeCheck = 1500;")
    L.append("\t\t\t\tTargetAttributes = {")
    L.append(f"\t\t\t\t\t{target} = {{")
    L.append("\t\t\t\t\t\tCreatedOnToolsVersion = 15.0;")
    L.append("\t\t\t\t\t};")
    L.append("\t\t\t\t};")
    L.append("\t\t\t};")
    L.append(f"\t\t\tbuildConfigurationList = {proj_cfg_list} /* Build configuration list for PBXProject \"{APP}\" */;")
    L.append("\t\t\tcompatibilityVersion = \"Xcode 14.0\";")
    L.append("\t\t\tdevelopmentRegion = en;")
    L.append("\t\t\thasScannedForEncodings = 0;")
    L.append("\t\t\tknownRegions = (")
    L.append("\t\t\t\ten,")
    L.append("\t\t\t\tBase,")
    L.append("\t\t\t);")
    L.append(f"\t\t\tmainGroup = {main_group};")
    L.append(f"\t\t\tproductRefGroup = {products_group} /* Products */;")
    L.append("\t\t\tprojectDirPath = \"\";")
    L.append("\t\t\tprojectRoot = \"\";")
    L.append("\t\t\ttargets = (")
    L.append(f"\t\t\t\t{target} /* {APP} */,")
    L.append("\t\t\t);")
    L.append("\t\t};")
    L.append("/* End PBXProject section */")

    # PBXResourcesBuildPhase
    L.append("")
    L.append("/* Begin PBXResourcesBuildPhase section */")
    L.append(f"\t\t{resources_phase} /* Resources */ = {{")
    L.append("\t\t\tisa = PBXResourcesBuildPhase;")
    L.append("\t\t\tbuildActionMask = 2147483647;")
    L.append("\t\t\tfiles = (")
    L.append("\t\t\t);")
    L.append("\t\t\trunOnlyForDeploymentPostprocessing = 0;")
    L.append("\t\t};")
    L.append("/* End PBXResourcesBuildPhase section */")

    # PBXSourcesBuildPhase
    L.append("")
    L.append("/* Begin PBXSourcesBuildPhase section */")
    L.append(f"\t\t{src_phase} /* Sources */ = {{")
    L.append("\t\t\tisa = PBXSourcesBuildPhase;")
    L.append("\t\t\tbuildActionMask = 2147483647;")
    L.append("\t\t\tfiles = (")
    for f in SWIFT_FILES:
        L.append(f"\t\t\t\t{build_files[f]} /* {f} in Sources */,")
    L.append("\t\t\t);")
    L.append("\t\t\trunOnlyForDeploymentPostprocessing = 0;")
    L.append("\t\t};")
    L.append("/* End PBXSourcesBuildPhase section */")

    # XCBuildConfiguration
    def common_build_settings():
        return [
            "\t\t\t\tALWAYS_SEARCH_USER_PATHS = NO;",
            "\t\t\t\tCLANG_ANALYZER_NONNULL = YES;",
            "\t\t\t\tCLANG_ENABLE_MODULES = YES;",
            "\t\t\t\tCLANG_ENABLE_OBJC_ARC = YES;",
            "\t\t\t\tENABLE_STRICT_OBJC_MSGSEND = YES;",
            "\t\t\t\tGCC_C_LANGUAGE_STANDARD = gnu17;",
            "\t\t\t\tSWIFT_VERSION = 5.0;",
            "\t\t\t\tSDKROOT = iphoneos;",
            "\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = 17.0;",
        ]

    def target_settings():
        return [
            "\t\t\t\tASSETCATALOG_COMPILER_GENERATE_ASSET_SYMBOLS = YES;",
            "\t\t\t\tCODE_SIGN_STYLE = Automatic;",
            "\t\t\t\tCURRENT_PROJECT_VERSION = 1;",
            "\t\t\t\tGENERATE_INFOPLIST_FILE = YES;",
            f"\t\t\t\tINFOPLIST_FILE = {APP}/Info.plist;",
            "\t\t\t\tINFOPLIST_KEY_UIApplicationSceneManifest_Generation = YES;",
            "\t\t\t\tINFOPLIST_KEY_UIApplicationSupportsIndirectInputEvents = YES;",
            "\t\t\t\tINFOPLIST_KEY_UILaunchScreen_Generation = YES;",
            "\t\t\t\tINFOPLIST_KEY_UISupportedInterfaceOrientations = \"UIInterfaceOrientationPortrait UIInterfaceOrientationLandscapeLeft UIInterfaceOrientationLandscapeRight\";",
            "\t\t\t\tLD_RUNPATH_SEARCH_PATHS = (",
            "\t\t\t\t\t\"$(inherited)\",",
            "\t\t\t\t\t\"@executable_path/Frameworks\",",
            "\t\t\t\t);",
            "\t\t\t\tMARKETING_VERSION = 1.0;",
            f"\t\t\t\tPRODUCT_BUNDLE_IDENTIFIER = {BUNDLE_ID};",
            "\t\t\t\tPRODUCT_NAME = \"$(TARGET_NAME)\";",
            "\t\t\t\tSWIFT_EMIT_LOC_STRINGS = YES;",
            "\t\t\t\tTARGETED_DEVICE_FAMILY = \"1,2\";",
        ]

    L.append("")
    L.append("/* Begin XCBuildConfiguration section */")
    # project debug
    L.append(f"\t\t{proj_debug} /* Debug */ = {{")
    L.append("\t\t\tisa = XCBuildConfiguration;")
    L.append("\t\t\tbuildSettings = {")
    for s in common_build_settings():
        L.append(s)
    L.append("\t\t\t\tDEBUG_INFORMATION_FORMAT = dwarf;")
    L.append("\t\t\t\tENABLE_TESTABILITY = YES;")
    L.append("\t\t\t\tGCC_OPTIMIZATION_LEVEL = 0;")
    L.append("\t\t\t\tONLY_ACTIVE_ARCH = YES;")
    L.append("\t\t\t\tSWIFT_ACTIVE_COMPILATION_CONDITIONS = DEBUG;")
    L.append("\t\t\t\tSWIFT_OPTIMIZATION_LEVEL = \"-Onone\";")
    L.append("\t\t\t};")
    L.append("\t\t\tname = Debug;")
    L.append("\t\t};")
    # project release
    L.append(f"\t\t{proj_release} /* Release */ = {{")
    L.append("\t\t\tisa = XCBuildConfiguration;")
    L.append("\t\t\tbuildSettings = {")
    for s in common_build_settings():
        L.append(s)
    L.append("\t\t\t\tDEBUG_INFORMATION_FORMAT = \"dwarf-with-dsym\";")
    L.append("\t\t\t\tENABLE_NS_ASSERTIONS = NO;")
    L.append("\t\t\t\tSWIFT_COMPILATION_MODE = wholemodule;")
    L.append("\t\t\t};")
    L.append("\t\t\tname = Release;")
    L.append("\t\t};")
    # target debug
    L.append(f"\t\t{target_debug} /* Debug */ = {{")
    L.append("\t\t\tisa = XCBuildConfiguration;")
    L.append("\t\t\tbuildSettings = {")
    for s in target_settings():
        L.append(s)
    L.append("\t\t\t};")
    L.append("\t\t\tname = Debug;")
    L.append("\t\t};")
    # target release
    L.append(f"\t\t{target_release} /* Release */ = {{")
    L.append("\t\t\tisa = XCBuildConfiguration;")
    L.append("\t\t\tbuildSettings = {")
    for s in target_settings():
        L.append(s)
    L.append("\t\t\t};")
    L.append("\t\t\tname = Release;")
    L.append("\t\t};")
    L.append("/* End XCBuildConfiguration section */")

    # XCConfigurationList
    L.append("")
    L.append("/* Begin XCConfigurationList section */")
    L.append(f"\t\t{proj_cfg_list} /* Build configuration list for PBXProject \"{APP}\" */ = {{")
    L.append("\t\t\tisa = XCConfigurationList;")
    L.append("\t\t\tbuildConfigurations = (")
    L.append(f"\t\t\t\t{proj_debug} /* Debug */,")
    L.append(f"\t\t\t\t{proj_release} /* Release */,")
    L.append("\t\t\t);")
    L.append("\t\t\tdefaultConfigurationIsVisible = 0;")
    L.append("\t\t\tdefaultConfigurationName = Release;")
    L.append("\t\t};")
    L.append(f"\t\t{target_cfg_list} /* Build configuration list for PBXNativeTarget \"{APP}\" */ = {{")
    L.append("\t\t\tisa = XCConfigurationList;")
    L.append("\t\t\tbuildConfigurations = (")
    L.append(f"\t\t\t\t{target_debug} /* Debug */,")
    L.append(f"\t\t\t\t{target_release} /* Release */,")
    L.append("\t\t\t);")
    L.append("\t\t\tdefaultConfigurationIsVisible = 0;")
    L.append("\t\t\tdefaultConfigurationName = Release;")
    L.append("\t\t};")
    L.append("/* End XCConfigurationList section */")

    L.append("\t};")
    L.append(f"\trootObject = {proj} /* Project object */;")
    L.append("}")

    out_dir = os.path.join(PROJ_DIR, f"{APP}.xcodeproj")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "project.pbxproj"), "w") as fh:
        fh.write("\n".join(L) + "\n")
    print("wrote", os.path.join(out_dir, "project.pbxproj"))


if __name__ == "__main__":
    main()

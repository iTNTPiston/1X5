# WARNING: This is a generated file
# You can edit it for prototyping, but please submit changes to the corresponding file in src/py

# This is a standalone bundler. You can use this script by itself
# The output is a minimized JSON, which can be distributed

# Usage: py gbundle.py <inputPath>
# Output: bundle.json

# === common.py ===

import yaml
import dukpy
import sys
import os
import json
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import http.server
import socketserver

# constants
BUNDLE_JSON = "bundle.json"
BUNDLE_RAW_JSON = "bundle.raw.json"
BUNDLER_JS = "bundler.js"

# Http stuff
class HostHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self,path):
        return BUNDLE_JSON
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super(HostHandler, self).end_headers()

def host_loop(port):
    with socketserver.TCPServer(("", port), HostHandler) as httpd:
        print(f"Hosting {BUNDLE_JSON} at localhost:" + str(port))
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Stopping...")

# Watcher Stuff
class Handler(FileSystemEventHandler):
    def __init__(self, inputFile, rebuildFunc):
        self.inputFile = inputFile
        self.rebuildFunc = rebuildFunc
    def on_any_event(self, event):
        if event.src_path.endswith(".yaml") or event.src_path.endswith(".ts"):
            print(f"Rebuilding... {self.inputFile}")
            self.rebuildFunc(self.inputFile)

def watch_start(inputFile, rebuildFunc):
    event_handler = Handler(inputFile, rebuildFunc)
    observer = Observer()
    observer.schedule(event_handler, ".", recursive=True)
    observer.start()
    print("Start watching changes")
    return observer

def watch_loop():
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print("Stopping...")  
            break
    
def watch_stop(observer):
    observer.stop()
    print("Stopped watching for changes")
    observer.join()

# Load Yaml Stuff
def rebundleHelper(inputPath, doEmitRaw, isCompact, bundleFunc):
    obj = {}
    loadYamlPath(inputPath, obj)
    if doEmitRaw:
        with open(BUNDLE_RAW_JSON, "w+") as out:
            json.dump(obj, out, indent=4)
            
        print(f"Emitted {BUNDLE_RAW_JSON}")

    bundled = bundleFunc(obj)

    with open(BUNDLE_JSON, "w+") as out:
        if isCompact:
            json.dump(bundled, out, separators=(',', ':'))
        else:
            json.dump(bundled, out, indent=4)
    print(f"Emitted {BUNDLE_JSON}")

def loadYamlPath(yamlPath, obj):
    if os.path.isfile(yamlPath) and yamlPath.endswith(".yaml"):
        obj.update(loadYamlFile(yamlPath))
    elif os.path.isdir(yamlPath):
        for subpath in os.listdir(yamlPath):
            loadYamlPath(os.path.join(yamlPath, subpath), obj)


def loadYamlFile(yamlFile):
    print(f"Loading {yamlFile}")
    with open(yamlFile, "r") as f:
        return yaml.load(f, Loader=yaml.FullLoader)

def tscompileAndInvokeBundler(obj):
    print("Compiling...")
    with open('src/ts/RouteScript.ts', "r") as tsSrc:
        
        bundlerJs = dukpy.typescript_compile(" ".join(line for line in tsSrc)  )
        with open(BUNDLER_JS, "w+") as bundlerOut:
            bundlerOut.write(bundlerJs)
        print(f"Emitted {BUNDLER_JS}")

    with open('src/js/system.js', "r") as systemSrc:
        systemJs = " ".join(line for line in systemSrc)

    with open('src/js/invoke.js', "r") as invokeSrc:
        invokeJs = " ".join(line for line in invokeSrc)
    return dukpy.evaljs([systemJs, bundlerJs, invokeJs], input=obj)

# === common.py ===
def __main__():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input> ")
        sys.exit(1)

    inputFile = sys.argv[1]
    print(f"Bundling... {inputFile}")
    rebuildBundle(inputFile)

def rebuildBundle(inputFile):
    rebundleHelper(inputFile, False, True, invokeJsBundle)

def invokeJsBundle(obj):
# JS_INJECT_NEXT_LINE
    return dukpy.evaljs("""//A dummy impl of SystemJS
 var exports = { };
 var System = {
     register: function(_, callback) {
         var module = callback(function(name, val){ exports[name] = val; });
         module.execute();
     }
 };
 
 // Expose bundler
 var bundler = function() { return exports["default"]; };System.register([], function(exports_1) {
    var TARGET_VERSION, __use__, switchSection, switchModule, switchStep, switchSinglePropertyObject, ENABLE_DEBUG, debugInfo, RouteScriptBundler;
    return {
        setters:[],
        execute: function() {
            // Target compiler version
            exports_1("TARGET_VERSION", TARGET_VERSION = "1.0.2");
            // Unbundled route script is what the bundler receives
            // The bundler processes __use__ directives and remove unused modules
            __use__ = "__use__";
            // Helper functions to encapsulate error handling when parsing route script
            exports_1("switchSection", switchSection = function (section, moduleHandler, errorHandler) {
                if (!section) {
                    return errorHandler("Not a valid section: " + section);
                }
                if (typeof section === "object" && !Array.isArray(section)) {
                    var _a = switchSinglePropertyObject(section, function (name, moduleOrExtend) {
                        // Need to further determine if module is a module or actually extend..
                        if (name.length > 0 && name[0] === "_") {
                            // if name starts with underscore, treat it as a step
                            return [undefined, section];
                        }
                        // Otherwise treat as section
                        return [name, moduleOrExtend];
                    }, function (errorString) {
                        return [errorString, undefined];
                    }), name = _a[0], module = _a[1];
                    if (!module) {
                        return errorHandler(name || "Unknown Error");
                    }
                    return moduleHandler(name, module);
                }
                //If falls through, must be unnamed section (section is a module)
                return moduleHandler(undefined, section);
            });
            exports_1("switchModule", switchModule = function (module, stringHandler, extendHandler, arrayHandler, errorHandler) {
                if (typeof module === "string") {
                    return stringHandler(module);
                }
                if (!module) {
                    return errorHandler("Not a valid step: " + JSON.stringify(module));
                }
                if (Array.isArray(module)) {
                    return arrayHandler(module);
                }
                return switchSinglePropertyObject(module, extendHandler, errorHandler);
            });
            exports_1("switchStep", switchStep = function (step, stringHandler, extendHandler, errorHandler) {
                if (typeof step === "string") {
                    return stringHandler(step);
                }
                if (!step) {
                    return errorHandler("Not a valid step: " + JSON.stringify(step));
                }
                if (Array.isArray(step)) {
                    return errorHandler("Step cannot be an array: " + JSON.stringify(step));
                }
                return switchSinglePropertyObject(step, extendHandler, errorHandler);
            });
            switchSinglePropertyObject = function (spo, okHandler, errorHandler) {
                if (!spo || typeof spo !== "object") {
                    return errorHandler("Not a valid step: " + JSON.stringify(spo));
                }
                var keys = Object.keys(spo);
                if (keys.length !== 1) {
                    return errorHandler("A valid step must have exactly 1 key, received: " + JSON.stringify(spo));
                }
                var key = keys[0];
                return okHandler(key, spo[key]);
            };
            // Debug switch. Only works on bundler side
            ENABLE_DEBUG = false;
            debugInfo = [];
            RouteScriptBundler = (function () {
                function RouteScriptBundler() {
                }
                RouteScriptBundler.prototype.bundle = function (script) {
                    return {
                        compilerVersion: TARGET_VERSION,
                        Project: this.ensureProject(script),
                        Route: this.bundleRoute(script, script.Route)
                    };
                };
                RouteScriptBundler.prototype.ensureProject = function (script) {
                    var project = {
                        Name: "Untitled Project",
                        Authors: [],
                        Url: "",
                        Version: "Unknown",
                        Description: "No Description",
                    };
                    if (script.Project) {
                        // Spread expression is not parsable in dukpy so here's the workaround
                        if (script.Project.Name) {
                            project.Name = script.Project.Name;
                        }
                        if (script.Project.Authors) {
                            project.Authors = script.Project.Authors;
                        }
                        if (script.Project.Url) {
                            project.Url = script.Project.Url;
                        }
                        if (script.Project.Version) {
                            project.Version = script.Project.Version;
                        }
                        if (script.Project.Description) {
                            project.Description = script.Project.Description;
                        }
                    }
                    return project;
                };
                RouteScriptBundler.prototype.bundleRoute = function (script, route) {
                    var _this = this;
                    // Make sure route is actually an array
                    if (!Array.isArray(route)) {
                        return ["(!=) Bundler Error: Route property must be an array"];
                    }
                    // First scan dependencies
                    var dependency = {};
                    route.forEach(function (section) {
                        switchSection(section, function (_, module) {
                            _this.scanDependencyForModule(dependency, "Route", module);
                        }, function () {
                            // Do not process dependency if error
                        });
                    });
                    for (var key in script) {
                        if (key !== "Project" && key !== "Configuration" && key !== "Route") {
                            this.scanDependencyForModule(dependency, key, script[key]);
                        }
                    }
                    // DFS to ensure no circular dependencies
                    var circularDependency = this.ensureNoCircularDependency(dependency, "Route", ["Route"]);
                    if (circularDependency) {
                        return ["(!=) Bundler Error: Circular dependency is detected, so the route is not processed. Please check all your __use__ directives to make sure there is no circular dependencies. Path hit: " + circularDependency];
                    }
                    var cache = {};
                    var bundled = this.bundleSections(script, route, cache);
                    //debug trace
                    if (ENABLE_DEBUG) {
                        bundled.push(JSON.stringify(cache));
                        bundled.push(JSON.stringify(debugInfo));
                    }
                    return bundled;
                };
                RouteScriptBundler.prototype.scanDependencyForModule = function (dependency, name, module) {
                    var _this = this;
                    switchModule(module, function (stringModule) {
                        _this.scanDependencyForStringStep(dependency, name, stringModule);
                    }, function () {
                        // Ignore preset extend
                    }, function (arrayModule) {
                        arrayModule.forEach(function (s) {
                            switchStep(s, function (stringStep) {
                                _this.scanDependencyForStringStep(dependency, name, stringStep);
                            }, function () {
                                // Ignore preset extend
                            }, function () {
                                // Do not process dependency if error
                            });
                        });
                    }, function () {
                        // Do not process dependency if error
                    });
                };
                RouteScriptBundler.prototype.scanDependencyForStringStep = function (dependency, name, step) {
                    var dep = this.getModuleNameFromStep(step);
                    if (dep) {
                        if (!dependency[name]) {
                            dependency[name] = [];
                        }
                        dependency[name].push(dep);
                    }
                };
                RouteScriptBundler.prototype.ensureNoCircularDependency = function (dependency, name, searchPath) {
                    if (!dependency[name]) {
                        //has no dependency
                        return undefined;
                    }
                    for (var i = 0; i < dependency[name].length; i++) {
                        var next = dependency[name][i];
                        // Make sure next is not already hit
                        for (var j = 0; j < searchPath.length; j++) {
                            if (next === searchPath[j]) {
                                return searchPath.join(" -> ") + " -> " + next;
                            }
                        }
                        // put next on stack
                        searchPath.push(next);
                        var recurResult = this.ensureNoCircularDependency(dependency, next, searchPath);
                        if (recurResult) {
                            return recurResult;
                        }
                        searchPath.pop();
                    }
                    return undefined;
                };
                RouteScriptBundler.prototype.bundleSections = function (script, sections, cache) {
                    var _this = this;
                    var returnArray = [];
                    sections.forEach(function (section) {
                        switchSection(section, function (name, module) {
                            debugInfo.push(module);
                            var bundledModule = _this.bundleModule(script, undefined, cache, module);
                            if (name) {
                                returnArray.push((_a = {}, _a[name] = bundledModule, _a));
                            }
                            else {
                                //Flatten the array if it is an array
                                switchModule(bundledModule, function (stringModule) {
                                    returnArray.push(stringModule);
                                }, function (preset, extend) {
                                    returnArray.push((_a = {}, _a[preset] = extend, _a));
                                    var _a;
                                }, function (arrayModule) {
                                    arrayModule.forEach(function (m) { return returnArray.push(m); });
                                }, function (errorString) {
                                    returnArray.push("(!=) Bundler Error: Error when bundling " + JSON.stringify(module) + ". Caused by: " + errorString);
                                });
                            }
                            var _a;
                        }, function (errorString) {
                            returnArray.push("(!=) Bundler Error: Error when bundling section " + JSON.stringify(section) + ". Caused by: " + errorString);
                        });
                    });
                    return returnArray;
                };
                RouteScriptBundler.prototype.bundleModule = function (script, name, cache, unbundledModule) {
                    var _this = this;
                    if (name && cache[name]) {
                        //Cache hit, return cached module
                        return cache[name];
                    }
                    // Cache miss, get unbundled from script
                    if (name) {
                        if (script[name] !== undefined) {
                            unbundledModule = script[name];
                        }
                        else {
                            unbundledModule = "(!=) Bundler Error: Cannot find module " + name;
                        }
                    }
                    else if (!unbundledModule) {
                        unbundledModule = "(!=) Bundler Error: Illegal Invocation of bundledModule(): Both name and unbundledModule are undefined. This is likely a bug in the bundler.";
                    }
                    var bundledModule = switchModule(unbundledModule, function (stringModule) {
                        if (stringModule.trim().substring(0, 7) === "__use__") {
                            var moduleName = stringModule.substring(7).trim();
                            return _this.bundleModule(script, moduleName, cache);
                        }
                        else {
                            return stringModule;
                        }
                    }, function (preset, extend) {
                        // No action here
                        return (_a = {},
                            _a[preset] = extend,
                            _a
                        );
                        var _a;
                    }, function (arrayModule) {
                        var returnArray = [];
                        arrayModule.forEach(function (s) {
                            switchStep(s, function (stringStep) {
                                var moduleName = _this.getModuleNameFromStep(stringStep);
                                if (moduleName) {
                                    var bundledModule_1 = _this.bundleModule(script, moduleName, cache);
                                    switchModule(bundledModule_1, function (stringModule) {
                                        returnArray.push(stringModule);
                                    }, function (preset, extend) {
                                        returnArray.push((_a = {}, _a[preset] = extend, _a));
                                        var _a;
                                    }, function (arrayModule) {
                                        // Flatten the array
                                        arrayModule.forEach(function (m) { return returnArray.push(m); });
                                    }, function (errorString) {
                                        returnArray.push("(!=) Bundler Error: Unexpected @279. Please contact developer. Message: " + errorString);
                                    });
                                }
                                else {
                                    returnArray.push(stringStep);
                                }
                            }, function (preset, extend) {
                                returnArray.push((_a = {}, _a[preset] = extend, _a));
                                var _a;
                            }, function (errorString) {
                                arrayModule.push("(!=) Bundler Error: Error when bundling " + JSON.stringify(s) + ". Caused by: " + errorString);
                            });
                        });
                        return returnArray;
                    }, function (errorString) {
                        return "(!=) Bundler Error: Error when bundling module with name " + name + ". Caused by: " + errorString;
                    });
                    if (name) {
                        cache[name] = bundledModule;
                    }
                    return bundledModule;
                };
                RouteScriptBundler.prototype.getModuleNameFromStep = function (step) {
                    if (step.trim().substring(0, 7) === __use__) {
                        return step.substring(7).trim();
                    }
                    return undefined;
                };
                return RouteScriptBundler;
            })();
            exports_1("default",new RouteScriptBundler());
        }
    }
});
// Input JSON passed from python
 bundler().bundle(dukpy.input);
""", input=obj)

__main__()

    
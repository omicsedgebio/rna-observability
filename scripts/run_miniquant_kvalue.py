#!/usr/bin/env python3
"""Build the pinned original miniQuant K-value units with a minimal local driver.

Does not alter upstream algorithms or import any quantification outcomes.
Upstream source remains ignored; this driver is project-authored.
"""
from pathlib import Path
import subprocess

root = Path('.cache/phase3a/miniquant_build/Augroup-miniQuant-c1b5a89/src').resolve()
driver = root/'phase3a_kvalue_driver.cc'
driver.write_text('''#include <calKvalue.hh>
#include <filesystem>
#include <iostream>
int main(int argc, char** argv) {
  if(argc!=3) {std::cerr<<"usage: kvalue annotation.gtf output_directory\\n";return 1;}
  ProgramOptions opt;
  opt.annotationFile=argv[1]; opt.outputFolder=argv[2]; opt.threads=2;
  opt.fraglen=235.0; opt.not_normalize_entry=false;
  opt.kvalue_entry_type=kvalue_entry_type_effective_length;
  std::filesystem::create_directories(opt.outputFolder);
  parallelCalKvalue(opt);
}
''')
sources = ['calKvalue.cc','annotationParser.cc','regionGenerator.cc','fileWriter.cc','util.cc']
binary = Path('.cache/phase3a/miniquant_kvalue').resolve()
command = ['clang++','-std=c++23','-O2','-ffunction-sections','-fdata-sections',
           '-I'+str(root/'include'),str(driver)] + [str(root/'src'/f) for f in sources]
# macOS strips unused quantification/LZ4 helper functions; Linux uses --gc-sections.
import platform
command += ['-Wl,-dead_strip' if platform.system()=='Darwin' else '-Wl,--gc-sections',
            '-pthread','-lz','-o',str(binary)]
print(' '.join(command), flush=True)
subprocess.run(command, check=True)
subprocess.run([str(binary), '.cache/phase3a/references/ensembl91.gtf',
                '.cache/phase3a/qc/miniquant'], check=True)

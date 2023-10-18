#!/usr/bin/python3

# SPDX-FileCopyrightText: 2023 Sebastien Jodogne, UCLouvain, Belgium
# SPDX-License-Identifier: GPL-3.0-or-later

# OHIF plugin for Orthanc
# Copyright (C) 2023 Sebastien Jodogne, UCLouvain, Belgium
#
# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


import gzip
import hashlib
import io
import os
import sys

if len(sys.argv) != 3:
    raise Exception('Usage: %s [source folder] [target C++]' % sys.argv[0])

SOURCE = sys.argv[1]
TARGET = sys.argv[2]

if not os.path.isdir(SOURCE):
    raise Exception('Nonexistent source folder: %s' % SOURCE)


def EncodeFileAsCString(f, variable, content):
    f.write('static const uint8_t %s[%d] = \n  "' % (variable, len(content) + 1))
    
    column = 0
        
    for c in content:
        
        if sys.version_info < (3, 0):
            # Python 2.7
            i = ord(c)
        else:
            # Python 3.x
            i = c
            
        if i < 32 or i >= 127 or i == ord('?'):
            f.write('\\{0:03o}'.format(i))
        elif i in [ ord('"'), ord('\\') ]:
            f.write('\\' + chr(i))
        else:
            f.write(chr(i))

        column += 1
        if column >= 120:
            f.write('"\n  "')
            column = 0
            
    f.write('";\n\n')


def WriteChecksum(f, variable, content):
    md5 = hashlib.md5(content).hexdigest()
    g.write('static const char* %s = "%s";\n\n' % (variable, md5))


with open(TARGET, 'w') as g:
    g.write('''
#include <stdint.h>
#include <Compression/GzipCompressor.h>
#include <OrthancException.h>
#include <Toolbox.h>

static void Uncompress(std::string& target, const void* data, size_t size, const std::string& md5Expected)
{
  Orthanc::GzipCompressor compressor;
  compressor.Uncompress(target, data, size);
  std::string md5Actual;
  Orthanc::Toolbox::ComputeMD5(md5Actual, target);
  if (md5Actual != md5Expected)
  {
    throw Orthanc::OrthancException(Orthanc::ErrorCode_CorruptedFile);
  }
}

''')    

    index = {}
    count = 0

    for root, dirs, files in os.walk(SOURCE):
        for f in files:
            fullPath = os.path.join(root, f)
            relativePath = os.path.relpath(os.path.join(root, f), SOURCE)
            variable = 'data_%06d' % count

            with open(fullPath, 'rb') as source:
                content = source.read()

            if sys.version_info < (3, 0):
                # Python 2.7
                fileobj = io.BytesIO()
                gzip.GzipFile(fileobj=fileobj, mode='w').write(content)
                compressed = fileobj.getvalue()
            else:
                # Python 3.x
                compressed = gzip.compress(content)

            EncodeFileAsCString(g, variable, compressed)
            WriteChecksum(g, variable + '_md5', content)

            index[relativePath] = variable

            count += 1
    
    g.write('void ReadStaticAsset(std::string& target, const std::string& path)\n')
    g.write('{\n')
    for (path, variable) in index.items():
        g.write('  if (path == "%s")\n' % path)
        g.write('  {\n')
        g.write('    Uncompress(target, %s, sizeof(%s) - 1, %s_md5);\n' % (variable, variable, variable))
        g.write('    return;\n')
        g.write('  }\n\n')

    g.write('  throw Orthanc::OrthancException(Orthanc::ErrorCode_InexistentItem, "Unknown OHIF resource: " + path);\n')
    g.write('}\n')

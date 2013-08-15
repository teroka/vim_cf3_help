#!/usr/bin/env python
# -*- coding: utf-8 -*- 

'''
Quickhax to update the help files.

To use this, you need to have github.com/cfengine/documentation.git
cloned to local dir and lynx installed. This uses the repo to check
what to crawl and get their relevant urls. Then call lynx to dump it.
'''

import os, sys, re, subprocess

home = os.environ['HOME']

# Tweak these if you need to.
cf3funcs = home + '/.vim/doc/cf3funcs.txt'
cf3specialvars = home + '/.vim/doc/cf3specialvars.txt'
cf3promisetypes = home + '/.vim/doc/cf3promisetypes.txt'
cf3docs = home + '/git/cfengine-documentation'
# This is the width of the help text we're outputting.
help_width = 78

url_prefix = 'https://cfengine.com/docs/3.5'
help_tag_prefix = 'cf3-'

# Check that we have the docs pulled
if not os.path.exists(cf3docs + '/.git'):
    print 'Unable to verify that cfengine/documentation was pulled'
    print 'Tried to find it from %s/.git' % cf3docs
    sys.exit()

def find_source_docs(srcdir):
    mdfiles = []
    for files in os.listdir(srcdir):
            if files.endswith('.markdown'):
                if os.path.exists(srcdir + os.path.splitext(files)[0]):
                    continue
                mdfiles.append(files)
    return mdfiles

def find_url_suffix(file):
    with open(file) as f:
        for line in f:
            regex = re.search('(?<=alias:\s)(\S+)',line)
            if regex:
                return regex.group()

def docparser(url,func,multifunc=False):
    if multifunc:
        func = func.replace('intrealstring','[int|real|string]')
        re_start = re.compile(r'^'+re.escape(func)+'$')
    else:
        re_start = re.compile(r'^'+func+'$')

    re_stop = re.compile(r'\s+\^\|$')
    rawdata = lynxdump(url).split('\n')
    line_start = None
    line_stop = None
    for idx, line in enumerate(rawdata):
        # start the content from our function
        if re.search(re_start,line):
            line_start=idx
        # end the content at the unicode up arrow
        if re.search(re_stop,line):
            line_stop=idx
    if line_start and line_stop:
        return rawdata[line_start:line_stop]
    else:
        print 'Unable to find the required patterns from %s' % url
        print 'Site layout changed?\n'
        return

def lynxdump(url):
    p = subprocess.Popen(['lynx', '-dump', '-display_charset=us-ascii',
        '-nolist', '-nonumbers', '-width',
        str(help_width), url], shell=False, stdout=subprocess.PIPE)
    return p.stdout.read()

def update_help(file,subdir):
    file = open(file, 'w')
    dir_suffix = '/reference/'+subdir+'/'
    srcfiles = find_source_docs(cf3docs + dir_suffix)
    for func in srcfiles:
        plain = os.path.splitext(func)[0]
        print 'Parsing help for %s' % plain
        url_suffix = find_url_suffix(cf3docs + dir_suffix + func)
        url = url_prefix + '/' + url_suffix
        file.write('=' * help_width + '\n')
        if re.search(r'.*intrealstring.*',plain):
            content = docparser(url,plain,True)
            if not content:
                continue
            if subdir == 'functions':
                headerstring = content[0]+'()'
            else:
                headerstring = content[0]
            file.write('%s' % headerstring )
            fhelp = plain.split('intrealstring')
            trio = [ 'int', 'real', 'string' ]
            mfunctags = []
            del content[0]
            for var in trio:
                mfunctags.append(fhelp[0] + var + fhelp[1])
            for i in mfunctags:
                help_tag = '{0:>{1}}'.format('*' + help_tag_prefix +
                        i + '*', help_width - len(headerstring))
                file.write('%s\n' % (help_tag))
                # zero out the list so alignment holds
                headerstring = []
            for i in content:
                file.write('%s\n' % i)
        else:
            content = docparser(url,plain,False)
            if not content:
                continue
            if subdir == 'functions':
                headerstring = content[0]+'()'
            else:
                headerstring = content[0]
            file.write('%s' % headerstring )
            # align the vim help *tag* to the right side and use our set width.
            help_tag = '{0:>{1}}'.format('*' + help_tag_prefix +
                    plain + '*', help_width - len(headerstring))
            file.write('%s\n' % (help_tag))
            del content[0]
            for i in content:
                file.write('%s\n' % i)
    file.close()

update_help(cf3funcs,'functions')
update_help(cf3specialvars,'special-variables')
update_help(cf3promisetypes,'promise-types')


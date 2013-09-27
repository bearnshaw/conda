from __future__ import print_function, division, absolute_import

import os
from conda.cli import common
from argparse import RawDescriptionHelpFormatter


descr = 'Create or extract a "bundle package" (EXPERIMENTAL)'


def configure_parser(sub_parsers):
    p = sub_parsers.add_parser(
        'bundle',
        formatter_class = RawDescriptionHelpFormatter,
        description = descr,
        help = descr,
    )
    cxgroup = p.add_mutually_exclusive_group()
    cxgroup.add_argument('-c', "--create",
                         action = "store_true",
                         help = "create bundle")
    cxgroup.add_argument('-x', "--extract",
                         action = "store",
                         help = "extact bundle located at PATH",
                         metavar = "PATH")
    cxgroup.add_argument("--metadump",
                         action = "store",
                         help = "dump metadata of bundle at PATH",
                         metavar = "PATH")

    common.add_parser_prefix(p)
    p.add_argument("--bundle-name",
                   action = "store",
                   help = "name of bundle",
                   metavar = 'NAME',
                   )
    p.add_argument("--data-path",
                   action = "store",
                   help = "path to data to be included in bundle",
                   metavar = "PATH"
                   )
    p.add_argument("--extra-meta",
                   action = "store",
                   help = "path to json file with additional meta-data no",
                   metavar = "PATH",
                   )
    p.add_argument("--no-env",
                   action = "store_true",
                   help = "no environment",
                   )
    p.add_argument("--outdir",
                   action = "store",
                   default = os.getcwd(),
                   help = "output directory, defaults to CWD",
                   metavar = "PATH",
                   )
    common.add_parser_json(p)
    p.set_defaults(func=execute)


def execute(args, parser):
    import sys
    import json

    import conda.bundle as bundle


    if not (args.create or args.extract or args.metadump):
        sys.exit("""Error:
    either one of the following options is required:
       -c/--create  -x/--extract  --metadump
    (see -h for more details)""")
    prefix = common.get_prefix(args)
    if args.no_env:
        prefix = None

    if args.create:
        if args.extra_meta:
            with open(args.extra_meta) as fi:
                extra = json.load(fi)
            if not isinstance(extra, dict):
                sys.exit('Error: no dictionary in: %s' % args.extra_meta)
        else:
            extra = None

        bundle.warn = []
        out_path = bundle.create_bundle(prefix, args.data_path,
                                        args.bundle_name, extra,
                                        output_dir=args.outdir)
        if args.json:
            d = dict(path=out_path, warnings=bundle.warn)
            json.dump(d, sys.stdout, indent=2, sort_keys=True)
        else:
            print(out_path)

    if args.extract:
        if args.data_path:
            sys.exit("Error: -x/--extract does not allow --data-path")
        if args.extra_meta:
            sys.exit("Error: -x/--extract does not allow --extra-meta")

        path = args.extract
        bundle.clone_bundle(path, prefix, args.bundle_name)

    if args.metadump:
        import tarfile

        path = args.metadump
        t = tarfile.open(path, 'r:*')
        try:
            f = t.extractfile(bundle.BMJ)
            sys.stdout.write(f.read())
            sys.stdout.write('\n')
        except KeyError:
            raise RuntimeError("no archive '%s' in: %s" % (bundle.BMJ, path))
        t.close()
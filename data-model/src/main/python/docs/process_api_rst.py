import os
import re
import argparse


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument('--path2docs',
                        dest='path2docs',
                        default=os.path.join(os.path.dirname(os.path.realpath(__file__)), "source", "api"),
                        help='Documents path')
    parser.add_argument('--to-drop',
                        dest='to_drop',
                        default=['Subpackages', 'Submodules', 'Module contents'],
                        help='Headers to drop')
    parser.add_argument('--create-git-ref',
                        dest='create_git_ref',
                        action="store_false",
                        help='If used, create default git doc file')
    # parser.add_argument('--create-install-ref',
    #                     dest='create_install_ref',
    #                     action="store_false",
    #                     help='If used, create default installation doc file')
    # parser.add_argument('--project-name',
    #                     dest='project_name',
    #                     help='Name of the project')
    # parser.add_argument('--root-name',
    #                     dest='root_name',
    #                     help='Name of the root folder of the project')

    #TODO: Creare automaticamente source/index.rst e source/install/index.rst

    args = parser.parse_args()

    if args.create_git_ref:
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "source", "git.rst"), 'w+') as fil:
            fil.write("**************\nGit Structure\n**************")
            fil.write("\n")
            fil.write("\nThe are several branches on the repository of the package:")
            fil.write("\n")
            fil.write("\n- ``Master`` carries the latest stable version of the package.")
            fil.write("\n- Other branches serves as development branches for various tasks and should be closed after "
                      "merging on master.")
            fil.write("\n")

    docs = os.listdir(args.path2docs)

    for filename in set(docs):

        in_module_contents = False
        line_num = 0
        reordered = []
        module_contents = []

        new_filename = filename

        with open(os.path.join(args.path2docs, filename), 'r') as fptr:
            for line in fptr:
                line = line.rstrip()
                discard = False

                line_num += 1

                if (len(line) > 0) and (line[0] not in ['.', '-', ' ']):
                    # pylint: disable=bad-continuation
                    line = re.split("\.", re.sub(" module", "", re.sub(" package", "", line)))[-1]
                    if in_module_contents:
                        in_module_contents = False

                for string in args.to_drop:
                    if line.find(string) == 0:
                        if string == 'Module contents':
                            in_module_contents = True
                        discard = True
                        # discard the underlines and a blank line too
                        _ = fptr.next()
                        _ = fptr.next()

                if in_module_contents and not discard:
                    module_contents.append(line)
                elif not discard:
                    reordered.append(line)

        with open(os.path.join(args.path2docs, new_filename), 'w') as fptr:
            fptr.write('\n'.join(reordered[:3]))
            fptr.write('\n')
            if module_contents:
                fptr.write('\n'.join(module_contents))
                fptr.write('\n')
                if len(module_contents[-1]) > 0:
                    fptr.write('\n')
            if reordered[3:]:
                fptr.write('\n'.join(reordered[3:]))
                fptr.write('\n')

# Copyright (C) 2021 Damona
#
#
# Inspired from the Conda project
#

function __damona_find_damona

    # if not defined (null string), let us try to find it
    if not test "$DAMONA_EXE_INTERN"
        # if DAMONA_EXE_INTERN is not set, we can figure out whether the command exists
        # using which damona. However, since we called this module, the damona()
        # function exists in the shell. Therefore, we first need to unset damona()
        # if we do so, it will not be set in the shell anymore. So, we must set it
        # but in a subshell using the ( ) syntax.

        set -e damona
        set -gx DAMONA_EXE_INTERN (which damona 2>/dev/null)
        set -gx DAMONA_SHELL_INFO "fish"

        if test -z "$DAMONA_EXE_INTERN"
            return
        end
    end
end



function damona


    if test "$DAMONA_EXE"
        set DAMONA_EXE_INTERN $DAMONA_EXE
    else
        set -e DAMONA_EXE_INTERN
        set -e DAMONA_SHELL_INFO
        __damona_find_damona
    end


    if not test "$DAMONA_EXE_INTERN"
        echo "DAMONA ERROR: 'damona' executable is not installed or could not be found. "
        echo "You can install it using "
        echo ""
        echo "    pip install damona "
        echo ""
        echo "If you know it is installed, you may set a DAMONA_EXE variable in your .bashrc"
        echo "or temporary in this shell using:"
        echo ""
        echo "    set DAMONA_EXE \"path_to_damona\""
        echo ""
        return 1
    end


    if [ (count $argv) -lt 1 ]
        eval $DAMONA_EXE_INTERN
    else
        set -l cmd $argv[1]
        set -e argv[1]
        switch $cmd
            case activate deactivate
                eval (eval $DAMONA_EXE_INTERN $cmd $argv)
            case install
                eval $DAMONA_EXE_INTERN $cmd $argv
            case '*'
                eval $DAMONA_EXE_INTERN $cmd $argv
        end
    end
end


# Autocompletions below


function __fish_damona_commands
    python -c "from damona.config import get_damona_commands; get_damona_commands()"
end


function __fish_damona_envs
  python -c "from damona import Environ; names=Environ().environment_names; print('\n'.join(names))"
end

function __fish_damona_packages
  damona list | awk '{print $1}'
end

function __fish_damona_needs_command
  set cmd (commandline -opc)
  if [ (count $cmd) -eq 1 -a $cmd[1] = 'damona' ]
    return 0
  end
  return 1
end

function __fish_damona_using_command
  set cmd (commandline -opc)
  if [ (count $cmd) -gt 1 ]
    if [ $argv[1] = $cmd[2] ]
      return 0
    end
  end
  return 1
end

# Damona commands
complete -f -c damona -n '__fish_damona_needs_command' -a '(__fish_damona_commands)'

# Commands that need environment as parameter
complete -f -c damona -n '__fish_damona_using_command activate' -a '(__fish_damona_envs)'
complete -f -c damona -n '__fish_damona_using_command deactivate' -a '(__fish_damona_envs)'

# Commands that need package as parameter
complete -f -c damona -n '__fish_damona_using_command install' -a '(__fish_damona_packages)'
#complete -f -c damona -n '__fish_damona_using_command uninstall' -a '(__fish_damona_packages)'
#complete -f -c damona -n '__fish_damona_using_command upgrade' -a '(__fish_damona_packages)'
#complete -f -c damona -n '__fish_damona_using_command update' -a '(__fish_damona_packages)'

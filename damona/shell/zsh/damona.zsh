

__damona_find_damona() {
    # if not defined (null string), let us try to find it
    if [[ -z $DAMONA_EXE_INTERN ]]; then

        # if DAMONA_EXE_INTERN is not set, we can figure out whether the command exists
        # using which damona. However, since we called this module, the damona()
        # function exists in the shell. Therefore, we first need to unset damona()
        # if we do so, it will not be set in the shell anymore. So, we must unset it
        # but in a subshell using the ( ) syntax.

        mycmd="$(unfunction damona; command -v damona 2>/dev/null)"
        my_status="$?"

        if [[ $my_status != 0 ]]; then
            echo "damona was not found. Install damona using 'pip install damona'"
            echo "$mycmd"
        elif [[ -z $mycmd ]]; then
            echo "damona was not found. Install damona using 'pip install damona'"
            echo "$mycmd"
        else
            export DAMONA_EXE_INTERN="$mycmd"

            # The SHELL environment variable typically stores the path to the default
            # login shell for the user. It is usually set when you start a new session
            # or login. However, it is not always accurate or updated if you switch
            # between different shells within the same session.
            # To determine the current shell in a more reliable way, you can use the ps
            # command with the -p flag and the process ID of the current shell.
            # the DAMONA_SHELL_INFO variable is set using the ps command with the process
            # ID of the current shell ($$). The -o comm= option specifies that only th
            # command name should be output. The t modifier is used to remove any leading
            # path components, ensuring that only the shell name is assigned to DAMONA_SHELL_INFO.
            export DAMONA_SHELL_INFO="$(ps -p $$ -o comm=)"
        fi
    fi
}


__damona_hashr() {
    if [ -n "${ZSH_VERSION:+x}" ]; then
        \rehash
    elif [ -n "${POSH_VERSION:+x}" ]; then
        :  # pass
    else
        \hash -r
    fi
}

__damona_activate() {

    \local cmd="$1"
    shift
    \local ask_damona

    ask_damona="$("$DAMONA_EXE_INTERN"  "$cmd" "$@")" || \return $?
    rc=$?

    \eval "$ask_damona"
    if [ $rc != 0 ]; then
        \export PATH
    fi

    __damona_hashr
}

__damona_deactivate() {
    \local cmd="$1"
    shift
    \local ask_damona
    ask_damona="$( "$DAMONA_EXE_INTERN" "$cmd" "$@")" || \return $?
    rc=$?

    \eval "$ask_damona"
    if [ $rc != 0 ]; then
        \export PATH
    fi

    #export PS1="$DAMONA_OLD_PS1 @P"
    __damona_hashr
}


__damona_verbose() {

    pattern="verbose=True"
    cmd="$(grep "$pattern" ~/.config/damona/damona.cfg)"

    # if not found, exit code is 1, if file does not exist, exit code 2.
    # if found, exit code 0
    info=$?
    if [[ $info = 1 ]]; then
        return 1
    fi

    pattern="verbose=true"
    cmd="$(grep "$pattern" ~/.config/damona/damona.cfg)"
    info=$?
    if [[ $info = 1 ]]; then
        return 1
    fi

    return 0
}


__welcome() {

  # Define color and formatting escape sequences
  RESET="\e[0m"          # Reset all attributes
  BOLD="\e[1m"           # Bold
  UNDERLINE="\e[4m"      # Underline
  GREEN="\e[32m"         # Green text
  YELLOW="\e[33m"        # Yellow text
  BLUE="\e[34m"          # Blue text
  BG_CYAN="\e[46m"       # Cyan background

  # Define the welcome message
  welcome_message="
  ${GREEN}${BOLD}======================================
          Welcome to DAMONA
  ======================================
  ${RESET}
  ${YELLOW}${UNDERLINE} \"Visit https://github.com/cokelaer/damona to help
   and https://damona.readthedocs.io for more info${RESET}
  "

  # Print the welcome message
  echo -e "$welcome_message"

}


__damona_setup() {

    # we will identify the executable here again and again. However, this is on purpose
    # This allows users to activate e.g. a new conda environment where another damona
    # standalone is available or hard-code the damona executable with DAMONA_EXE variable.
    __damona_verbose
    verbose=$?

    if [[ $verbose = 1 ]]; then
       __welcome
    fi

    if [ "$DAMONA_EXE" ]; then
        if [[ $verbose = 1 ]]; then
            echo "Using user-defined DAMONA_EXE"
        fi
        DAMONA_EXE_INTERN=$DAMONA_EXE
    else
        # make sure we use the correct executable
        #if [[ $verbose = 1 ]]; then
        #    echo "Searching for damona executable"
        #fi
        unset DAMONA_EXE_INTERN
        unset DAMONA_SHELL_INFO
        __damona_find_damona

    fi

    if [[ -z "$DAMONA_EXE_INTERN" ]]; then
        echo "DAMONA ERROR: 'damona' executable is not installed or could not be found. "
        echo "If you know it is installed, you may set a DAMONA_EXE variable in your .bashrc"
        echo "or temporary in this shell using:"
        echo ""
        echo "    export DAMONA_EXE=\"path_to_damona\""
        echo ""
        return 1
    fi

    if [[ $verbose = 1 ]]; then
        echo "Using Damona executable: $DAMONA_EXE_INTERN"
    fi

}


# specificity zsh for the shift function
# In zsh, the shift command requires the shift count to be less than or equal to the number of 
# positional parameters ($#). If the shift count exceeds the number of positional parameters, 
# zsh produces a warning similar to the one you mentioned: "shift count must be <= $#" (where 
# the line number may vary).
# This modification redirects the warning message to /dev/null and ensures that zsh does not 
# produce the warning when the shift count exceeds the number of positional parameters. 
# The || : at the end ensures that the line does not produce an error if the shift command fails.

damona () {

  __damona_setup

    if [[ "$#" -lt 1 ]]; then
        "$DAMONA_EXE_INTERN"
    else
        \local cmd="$1"
        shift 2>/dev/null || :

        # for the activate/deactivate special cases, user may provide 
        # --level DEBUG  before the command.
        case "$cmd" in
            --level)
                \local level="$1"
                shift 2>/dev/null || :
                \local maincmd="$1"
                shift 2>/dev/null || :

                case "$maincmd" in
                    activate)
                        __damona_activate --level "$level" "$maincmd" "$@"
                        ;;
                    deactivate)
                        __damona_deactivate --level "$level" "$maincmd" "$@"
                        ;;
                    *)
                        "$DAMONA_EXE_INTERN" --level "$level" "$maincmd" "$@"
                        \local t1=$?
                        return $t1
                        ;;
                 esac
            ;;
            activate)
                __damona_activate "$cmd" "$@"
                ;;
            deactivate)
                \local maincmd="$1"
                shift 2>/dev/null || :
                case "$maincmd" in 
                    --help)
                        ask_damona="$( "$DAMONA_EXE_INTERN" "deactivate" "--help")"
                        echo "$ask_damona"
                        ;;
                    *)
                        __damona_deactivate "deactivate" "$maincmd" "$@"
                        ;;
                        esac
                ;;
            *)
                "$DAMONA_EXE_INTERN"  "$cmd" "$@"
                \local t1=$?
                return $t1
                ;;
        esac
    fi
}

# This DAMONA_PATH is used to stored images and environments (including
# binaries). If it is already set by a user, no need to define it, otherwise the
# default is in the home of the user.
if [ -z $DAMONA_PATH ]; then
    export DAMONA_PATH="${HOME}/.config/damona"
fi




#if [ -z "${DAMONA_SHLVL+x}" ]; then
#    \export DAMONA_SHLVL=0
#
#    # We're not allowing PS1 to be unbound. It must at least be set.
#    # However, we're not exporting it, which can cause problems when starting a second shell
#    # via a first shell (i.e. starting zsh from bash).
#    if [ -z "${PS1+x}" ]; then
#        PS1=
#    fi
#fi



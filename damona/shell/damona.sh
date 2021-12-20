

__damona_find_damona() {
    # if not defined (null string), let us try to find it
    if [ -z $DAMONA_EXE_INTERN ]; then

        # if DAMONA_EXE_INTERN is not set, we can figure out whether the command exists
        # using which damona. However, since we called this module, the damona()
        # function exists in the shell. Therefore, we first need to unset damona()
        # if we do so, it will not be set in the shell anymore. So, we must unset it
        # but in a subshell using the ( ) syntax.

        mycmd="$( unset damona; which damona 2>/dev/null )"
        status=$?

        if [ $status != 0 ]; then
            echo "damona not found."
            echo "$mycmd"
        elif [ -z $mycmd ]; then
            echo "damona not found."
            echo "$mycmd"
        else
            export DAMONA_EXE_INTERN="$mycmd"
        fi
    #else
    #    echo "Using Damona executable: $DAMONA_EXE_INTERN"
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

    pattern="quiet=True"
    cmd="$(grep "$pattern" ~/.config/damona/damona.cfg)"
    # if not found, exit code is 1, if file does not exist, exit code 2.
    # if found, exit code 0
    info=$?
    if [ $info != 0 ]; then
        pattern="quiet=true"
        cmd="$(grep "$pattern" ~/.config/damona/damona.cfg)"
        info=$?
        if [ $info != 0 ]; then
            return 0
        fi
    fi

    return 1
}




damona() {

    # we will identify the executable here again and again. However, this is on purpose
    # This allows users to activate e.g. a new conda environment where another damona
    # standalone is available or hard-code the damona executable with DAMONA_EXE variable.
    __damona_verbose
    verbose=$?

    if [ $verbose == 1 ]; then
        echo "  ====================================================="
        echo "                   Welcome to Damona                   "
        echo "  ====================================================="
        echo
    fi

    if [ "$DAMONA_EXE" ]; then
        if [ $verbose == 1 ]; then
            echo "Using user-defined DAMONA_EXE"
        fi
        DAMONA_EXE_INTERN=$DAMONA_EXE
    else
        # make sure we use the correct executable
        if [ $verbose == 1 ]; then
            echo "Searching for damona executable"
        fi
        unset DAMONA_EXE_INTERN
        __damona_find_damona
    fi

    if [ -z "$DAMONA_EXE_INTERN" ]; then
        echo "DAMONA ERROR: 'damona' executable is not installed or could not be found. "
        echo "If you know it is installed, you may set a DAMONA_EXE variable in your .bashrc"
        echo "or temporary in this shell using:"
        echo ""
        echo "    export DAMONA_EXE=\"path_to_damona\""
        echo ""
        return 1
    fi

    if [ $verbose == 1 ]; then
        echo "Using Damona executable: $DAMONA_EXE_INTERN"
    fi

    if [ "$#" -lt 1 ]; then
        "$DAMONA_EXE_INTERN"
    else
        \local cmd="$1"
        shift

        # for the activate/deactivate special cases, user may provide 
        # --level DEBUG  before the command.
        case "$cmd" in
            --level)
                \local level="$1"
                shift
                \local maincmd="$1"
                shift

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
                shift
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



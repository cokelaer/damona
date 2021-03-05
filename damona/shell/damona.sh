

__damona_find_damona() {
    if [ -f $DAMONA_EXE ]; then
        mycmd="$(which damona 1>/dev/null 2>/dev/null)"
        status=$?

        if [ $status != 0 ]; then
            pattern="show_init_warning_message=False"
            cmd="$(grep -q "$pattern" ~/.config/damona/damona.cfg)"
            info=$?
            if [ $info != 0 ]; then
                echo "damona was not found in your path but a config file was found. It you want to ignore this message, edit the config file in .config/damona/damona.cfg and set show_init_warning_message=False"
            fi
        else
            export DAMONA_EXE="$mycmd"
        fi
    fi
}
# we should set the DAMONA_EXE variable if not set already
__damona_find_damona


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

    echo "$cmd"
    echo "$@"

    ask_damona="$("$DAMONA_EXE"  "$cmd" "$@")" || \return $?
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
    ask_damona="$( "$DAMONA_EXE" "$cmd" "$@")" || \return $?
    rc=$?

    \eval "$ask_damona"
    if [ $rc != 0 ]; then
        \export PATH
    fi

    __damona_hashr
}




damona() {

    if [ -z "$DAMONA_EXE" ]; then
        echo "You must define the DAMONA_EXE variable to point towards the damona executable"
        echo "Set it in your .bashrc or temporary in this shell."
        echo "export DAMONA_EXE=\"path_to_damona\""
        #return
    fi

    if [ "$#" -lt 1 ]; then
        "$DAMONA_EXE"
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
                        "$DAMONA_EXE" --level "$level" "$maincmd" "$@"
                        \local t1=$?
                        return $t1
                        ;;
                 esac
            ;;
            activate)
                __damona_activate "$cmd" "$@"
                ;;
            deactivate)
                __damona_deactivate "$cmd" "$@"
                ;;
            *)
                "$DAMONA_EXE"  "$cmd" "$@"
                \local t1=$?
                return $t1
                ;;
        esac
    fi
}

# we activate the base environment
# This DAMONA_PATH is used to stored images and environements (including
# binaries). If it is already set by a user, no need to define it, otherwise the
# default is in the home of the user.
if [ -f $DAMONA_PATH ]; then
    export DAMONA_PATH="${HOME}/.config/damona"
fi
#export PATH=${DAMONA_PATH}/bin:$PATH



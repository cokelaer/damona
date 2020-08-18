

__damona_find_damona() {
    if [ -f $DAMONA_EXE ]; then
        mycmd="$(which damona)"
        status=$?

        if [ $status != 0 ]; then
            echo "damona executable could not be found in your PATH"
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
    ask_damona="$("$DAMONA_EXE"  "$cmd" "$@")" || \return $?
    rc=$?

    \eval "$ask_damona"
    if [ $rc != 0 ]; then
        \export PATH
    fi
    __damona_hashr
}


__damona_deactivate() {
    \local ask_damona
    ask_damona="$( "$DAMONA_EXE" deactivate )" || \return $?
    \eval "$ask_damona"
    __damona_hashr
}

_damona_completion() {
    local IFS=$'
'
    COMPREPLY=( $( env COMP_WORDS="${COMP_WORDS[*]}" \
                   COMP_CWORD=$COMP_CWORD \
                   _DAMONA_COMPLETE=complete $1 ) )
    return 0
}

_damona_completionetup() {
    local COMPLETION_OPTIONS=""
    local BASH_VERSION_ARR=(${BASH_VERSION//./ })
    # Only BASH version 4.4 and later have the nosort option.
    if [ ${BASH_VERSION_ARR[0]} -gt 4 ] || ([ ${BASH_VERSION_ARR[0]} -eq 4 ] && [ ${BASH_VERSION_ARR[1]} -ge 4 ]);
    then
        COMPLETION_OPTIONS="-o nosort"
    fi

    complete $COMPLETION_OPTIONS -F _damona_completion damona
}

_damona_completionetup;



damona() {

    if [ -z "$DAMONA_EXE" ]; then
        echo "You must define the DAMONA_EXE variable to point towards the damona executable"
        echo "Set it in your .bashrc or in this shell"
        echo "export DAMONA_EXE=\"path_to_damona\""
        return
    fi

    if [ "$#" -lt 1 ]; then
        "$DAMONA_EXE"
    else
        \local cmd="$1"
        shift
        case "$cmd" in
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
export DAMONA_ENV="${HOME}/.config/damona"
export PATH=${DAMONA_ENV}/bin:$PATH



set -ex

if [[ "$(uname -s)" == 'Darwin' ]]; then
    if which pyenv > /dev/null; then
        eval "$(pyenv init -)"
    fi
    pyenv activate conan
fi

if [[ "$TRAVIS_TEST_RESULT" == 0 ]]; then
  python -c "from citools.githubtools import set_build_status, State; set_build_status('build_trigger.json', '$CONAN_BLDRVNLW_TOKEN', '$TRAVIS_BUILD_WEB_URL', 'Travis', State.success)"
else
  python -c "from citools.githubtools import set_build_status, State; set_build_status('build_trigger.json', '$CONAN_BLDRVNLW_TOKEN', '$TRAVIS_BUILD_WEB_URL', 'Travis', State.failure)"
fi
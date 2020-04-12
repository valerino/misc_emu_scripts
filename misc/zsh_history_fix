#!/usr/bin/env sh
# must be run through zsh!

echo '[.] fixes a corrupt ~/.zsh_history'
mv ~/.zsh_history ~/.zsh_history_bad
strings ~/.zsh_history_bad > ~/.zsh_history
fc -R ~/.zsh_history
rm ~/.zsh_history_bad
echo '[.] Done!'

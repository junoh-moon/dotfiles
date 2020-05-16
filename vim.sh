#!/bin/bash

source ./include.sh


border "Entering vim plugins installaion phase"


if !(npm --version &> /dev/null) || !(python3 -m pip --version &> /dev/null) || !(vim --version &> /dev/null); then
	echo "To install vim settings, npm, vim, and pip3 is needed"
	echo "Please install them and run it again"
	exit 1
fi

## Check for accessibility
if [[ $(whoami) == "root" ]]; then
	sudo=""
else
	sudo="sudo"
fi

folder=$(pwd)
ln -fs "$folder"/.vimrc $HOME/.vimrc

#vim 설정
printf "Installing yarn... "
measure $sudo npm install -g yarn
mkdir -p ~/.config/coc/extensions
git clone https://github.com/neoclide/coc.nvim.git $HOME/.vim/plugged/coc.nvim
cd $HOME/.vim/plugged/coc.nvim &&  yarn install --frozen-lockfile
cd $folder

vim --not-a-term -c PlugInstall -c quitall

#Promptline 설정
$sudo chmod +w $HOME
rm -f $HOME/.promptline.sh && vim -c "PromptlineSnapshot $HOME/.promptline.sh airline" -c quitall

# coc.nvim 설정



printf "Installing coc plugins... "
cd ~/.config/coc/extensions
if [ ! -f package.json ]; then
	echo '{"dependencies":{}}'> package.json
fi

ln -sf "$folder"/coc-settings.json $HOME/.vim/
ln -sf "$folder"/.coc.vimrc $HOME/
mkdir -p $HOME/.config/yapf
ln -sf "$folder"/py_style $HOME/.config/yapf/style

measure $sudo npm i -g bash-language-server \; \
	python3 -m pip install --user python-language-server[yapf,pylint,rope] \; \
	npm install --global-style --ignore-scripts --no-bin-links --no-package-lock --only=prod \
		coc-python coc-java coc-cmake coc-git coc-markdownlint coc-texlab coc-terminal \
		coc-tsserver coc-snippets coc-calc coc-json && \

#vim -c 'CocInstall -sync coc-python coc-java coc-cmake coc-git coc-markdownlint coc-texlab coc-terminal coc-tsserver' -c quitall

cd $folder

# coc-texlab 설정
## 컴파일시마다 sumatrapdf에게 알려주는 역할
ln -fs "$folder"/.latexmkrc $HOME/.latexmkrc

border "Package vim plugins installation phase completed! 😉"
printf "\n\n"


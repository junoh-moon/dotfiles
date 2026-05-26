"key mapping
let mapleader=","

autocmd BufNewFile,BufRead .env,.*.env set filetype=env

autocmd FileType typescript setlocal tabstop=2 softtabstop=2 shiftwidth=2 expandtab
autocmd FileType typescriptreact setlocal tabstop=2 softtabstop=2 shiftwidth=2 expandtab
autocmd FileType javascript setlocal tabstop=2 softtabstop=2 shiftwidth=2 expandtab
autocmd FileType javascriptreact setlocal tabstop=2 softtabstop=2 shiftwidth=2 expandtab

autocmd FileType yaml set cursorcolumn
autocmd FileType python	set cursorcolumn

" Enable 24bit true color
set termguicolors

" Correct RGB escape codes for vim inside tmux
if &term =~ '^\%(screen\|tmux\)'
  " nvim's tree-sitter has a problem that cannot parse the lines below (t_f8, t_8b).
  " Thankfully, adding a comment can prevent this odd error.
  " That's why I added silly comments below.
  let &t_8f = "\<ESC>[38;2;%lu;%lu;%lum"
  " above: foreground color (r, g, b) 
  let &t_8b = "\<ESC>[48;2;%lu;%lu;%lum"
  " above: background color (r, g, b) 
endif

silent! colorscheme coehler


syntax on
set nocompatible " 오리지날 VI와 호환하지 않음
set hlsearch
set incsearch
set lazyredraw
set laststatus=2
set ignorecase
set smartcase
set autoindent  " 자동 들여쓰기
set cindent " C 프로그래밍용 자동 들여쓰기
set smartindent " 스마트한 들여쓰기
set wrap " 문장이 한 줄로 넘어갈 경우 그 다음줄에 이어서 표시
set linebreak " wrap 사용시 단어 단위로 다음줄로 넘어가기
set nowrapscan " 검색할 때 문서의 끝에서 처음으로 안돌아감
set nobackup " 백업 파일을 안만듬
set noswapfile "스왑 파일을 만들지 않는다.
set visualbell " 키를 잘못눌렀을 때 화면 프레시
set belloff+=esc
set ruler " 화면 우측 하단에 현재 커서의 위치(줄,칸) 표시
set shiftwidth=4 " 자동 들여쓰기 4칸
set ts=4
set number " 행번호 표시, set nu 도 가능
set fencs=ucs-bom,utf-8,cp949,euc-kr
set conceallevel=2	" Basically prettify keywords if possible
set concealcursor=	" Disable syntax for current cursor line
set signcolumn=auto
set guicursor=      " Let vim\neovim respect Terminal's cursor shape
set mouse=          " Disable mouse

"set cursorcolumn	" Visualize vertical cursor line
"set cursorline		" Visualize horizontal cursor line
"set tenc=utf-8	  " 터미널 인코딩

set spelllang=en,cjk
set spellsuggest=best,9
" In LaTeX mode, enable spellcheck
" If you want to register user-defined words, press zg on the word.
aug tex
	au FileType tex set spell
aug end

aug elixir
	" tabstop:		Width of tab character.
	" softtabstop:	Fine tunes the amount of white space to be added.
	" shiftwidth:	Determines the amount of whitespace to add in normal mode.
	" expandtab:	Use spaces instead of tabs. 
	au FileType elixir setlocal tabstop=2 softtabstop=2 shiftwidth=2 expandtab
aug end

" Set filetype for custom extensions
autocmd! BufEnter *.shrc : set filetype=sh
autocmd! BufEnter *.shinit : set filetype=sh
autocmd! BufEnter *.nsp :set filetype=json
autocmd! BufEnter coc-settings.json :set filetype=jsonc

"https://vim.fandom.com/wiki/Make_buffer_modifiable_state_match_file_readonly_state
function! UpdateModifiable()
	if !exists("b:setmodifiable")
		let b:setmodifiable = 0
	endif
	if &readonly
		if &modifiable
			setlocal nomodifiable
			let b:setmodifiable = 1
		endif
	else
		if b:setmodifiable
			setlocal modifiable
		endif
	endif
endfunction

autocmd BufReadPost * call UpdateModifiable()
if index(["dosbatch", "ps1"], &filetype) < 0
	"newline 형식이 dos (<CR><NL>)인경우 unix형식(<NL>)로 변경 후 저장
	autocmd BufReadPost * if &modifiable &&  &l:ff!="unix" | setlocal ff=unix | %s/\r//ge | write | endif
endif
"euc-kr 혹은 cp949로 입력이 들어온 경우, utf-8로 변환 후 저장.
autocmd BufReadPost * if &modifiable && &l:fenc=="euc-kr" | setlocal fenc=utf-8 | write | endif
autocmd BufReadPost * if &modifiable && &l:fenc=="cp949"  | setlocal fenc=utf-8 | write | endif

" 마지막 편집 위치 복원 기능
au BufReadPost *
\ if line("'\"") > 0 && line("'\"") <= line("$") |
\   exe "norm g`\"" |
\ endif

"Vimdiff시 read only 무시
if &diff
	set noreadonly
endif

"파일이 변경될 때 마다 자동으로 버퍼 갱신
set autoread
au CursorHold * checktime

"vim의 검색 기능을 이용할 시 검색 결과를 항상 중앙에 배치한다.
nmap n nzz
nmap <S-n> <S-n>zz

nnoremap <leader>q : bp!<CR> " 쉼표 + q : 이전 탭
nnoremap <leader>w : bn!<CR> " 쉼표 + w : 다음 탭
nnoremap <leader>d : bp <BAR> bd #<CR> " 쉼표 + d : 탭 닫기
nnoremap <leader>e <C-W>w " 쉼표 + w : 다음 창



" ------------------------------------------------------------------------------
" Pipe selected visual block -- CHARACTER WISE -- to command.
" <C-u> after colon is used to cancel " '<,'> ", and it will be piped to
" command's stdin.

xnoremap <leader>c :<C-u> call PipeRangedSelection()<CR>

function! PipeRangedSelection()
	let cmd = input("Command: ")
	redraw
	echo system(cmd, GetVisualSelection(visualmode()))
endfunction


" Forked from https://stackoverflow.com/a/61486601
function! GetVisualSelection(mode)
	" call with visualmode() as the argument
	let [line_start, column_start] = getpos("'<")[1:2]
	let [line_end, column_end]     = getpos("'>")[1:2]
	let lines = getline(line_start, line_end)
	if a:mode ==# 'v'
		" Must trim the end before the start, the beginning will shift left.
		let lines[-1] = lines[-1][: column_end - (&selection == 'inclusive' ? 1 : 2)]
		let lines[0] = lines[0][column_start - 1:]
	elseif  a:mode ==# 'V'
		" Line mode no need to trim start or end
	elseif  a:mode == "\<c-v>"
		" Block mode, trim every line
		let new_lines = []
		let i = 0
		for line in lines
			let lines[i] = line[column_start - 1: column_end - (&selection == 'inclusive' ? 1 : 2)]
			let i = i + 1
		endfor
	else
		return ''
	endif
	"for line in lines
	"    echom line
	"endfor
	return join(lines, "\n")
endfunction


" ------------------------------------------------------------------------------
" FIX: ssh from wsl starting with REPLACE mode
" https://stackoverflow.com/a/11940894
if $TERM =~ 'xterm-256color'
	set noesckeys
endif

highlight Comment cterm=italic gui=italic

highlight Statement cterm=italic gui=italic
highlight Conditional cterm=italic gui=italic
highlight Repeat cterm=italic gui=italic
highlight Label cterm=italic gui=italic
highlight Operator cterm=italic gui=italic
highlight Keyword cterm=italic gui=italic
highlight Exception cterm=italic gui=italic

highlight Type cterm=italic gui=italic
highlight StorageClass cterm=italic gui=italic
highlight Structure cterm=italic gui=italic
highlight Typedef cterm=italic gui=italic

if has("patch-8.1.0360")
	" Myer, a default diff algorithm, sucks

	" Turn off whitespaces compare and folding in vimdiff
	set diffopt+=iwhite
	set diffopt+=vertical

	" Show filler lines, to keep the text synchronized with a window that has inserted lines at the same position
	set diffopt+=filler

	set diffopt+=internal,algorithm:patience
	set diffopt+=indent-heuristic
	set diffopt+=algorithm:histogram
endif

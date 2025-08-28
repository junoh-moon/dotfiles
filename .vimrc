" Vim-plug 자동 설치용
" START - Setting up Vundle - the vim plugin bundler
if empty(glob('~/.vim/autoload/plug.vim'))
	silent !curl -fLo ~/.vim/autoload/plug.vim --create-dirs
				\ https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
	autocmd VimEnter * PlugInstall --sync | source $MYVIMRC
endif

"key mapping
let mapleader=","

call plug#begin('~/.vim/plugged/')
" alternatively, pass a path where Vundle should install plugins
"call vundle#begin('~/some/path/here')

Plug 'tpope/vim-fugitive', { 'tag': '*' }

Plug 'tommcdo/vim-fugitive-blame-ext'


if !has('nvim')
  "256색 콘솔에서 gui용 테마 적용을 가능하게 함
  Plug 'godlygeek/csapprox'
endif

"테마(theme)
if has('nvim')
	Plug 'rktjmp/lush.nvim'
	Plug 'shaunsingh/nord.nvim'
endif
Plug 'tomasr/molokai'
Plug 'sainnhe/gruvbox-material'
Plug 'pineapplegiant/spaceduck', { 'branch': 'main' }
Plug 'NLKNguyen/papercolor-theme'
Plug 'danilo-augusto/vim-afterglow'
Plug 'vigoux/oak'
Plug 'mcchrish/zenbones.nvim' "https://vimcolorschemes.com/mcchrish/zenbones.nvim


Plug 'vim-airline/vim-airline'
Plug 'vim-airline/vim-airline-themes'
let g:airline#extensions#tabline#enabled = 1			  " vim-airline 버퍼 목록 켜기
let g:airline#extensions#tabline#fnamemod = ':t'		  " vim-airline 버퍼 목록 파일명만 출력
let g:airline#extensions#tabline#buffer_nr_show = 1	   " buffer number를 보여준다
let g:airline#extensions#tabline#buffer_nr_format = '%s:' " buffer number format
set laststatus=2 " turn on bottom bar

let g:airline#extensions#whitespace#enabled = 0 		"Disable trailing whitespace warning
let g:airline_theme = 'tomorrow'

let g:airline_powerline_fonts = 1
if !exists('g:airline_symbols')
	let g:airline_symbols = {}
endif

" 여기에 LSP 관련 내용 추가
Plug 'neoclide/coc.nvim', {'branch': 'release'}
"Plug 'neoclide/coc.nvim', {'do': 'yarn install --frozen-lockfile'}
silent! source ~/.coc.vimrc
let g:coc_global_extensions = [
			\'coc-biome',
			\'coc-calc',
			\'coc-clangd',
			\'coc-cmake',
			\'coc-elixir',
			\'coc-floaterm',
			\'coc-git',
			\'coc-go',
			\'coc-java',
			\'coc-json',
			\'coc-markdownlint',
			\'coc-pairs',
			\'coc-perl',
			\'coc-pyright',
			\'coc-rust-analyzer',
			\'coc-sh',
			\'coc-snippets',
			\'coc-snippets',
			\'coc-sql',
			\'coc-sumneko-lua',
			\'coc-terminal',
			\'coc-toml',
			\'coc-tsserver',
			\'coc-vimlsp',
			\'coc-vimtex',
			\'coc-xml',
			\'coc-yaml',
			\'https://github.com/cstrap/python-snippets',
			\'https://github.com/rafamadriz/friendly-snippets@main',
			\]


"tmux airline
Plug 'edkolev/tmuxline.vim'
let g:airline#extensions#tmuxline#enabled = 0

"Git graph
Plug 'rbong/vim-flog'


Plug 'Yggdroot/indentLine'
let g:indentLine_setConceal = 0 " Respect my conceal option!
let g:indentLine_char = '┊'
set list lcs=tab:\┊\ 

"fzf 설정
Plug 'junegunn/fzf'
Plug 'junegunn/fzf.vim'
nnoremap <leader><C-n> :Files<CR>

if executable("rg")
	nnoremap <leader>r :Rg!<CR>
else
	nnoremap <leader>r :Ag!<CR>
endif

" Only focus on file contents, not file names
command! -bang -nargs=* Ag call fzf#vim#ag(<q-args>, {'options': '--delimiter : --nth 4..'}, <bang>0)
command! -bang -nargs=* Rg
  \ call fzf#vim#grep("rg --column --line-number --no-heading --color=always --smart-case ".shellescape(<q-args>), 1,
  \   fzf#vim#with_preview({'options': '--delimiter : --nth 4..'}), <bang>0)

" #######################
" #####   Folding   #####
" #######################
if has("nvim")
	Plug 'kevinhwang91/promise-async'
	Plug 'kevinhwang91/nvim-ufo'
else
	set foldmethod=syntax
	" Support python folding
	Plug 'tmhedberg/SimpylFold'
	" Fold faster
	Plug 'Konfekt/FastFold'
endif


" #######################
" # Syntax highlighting #
" #######################
if has("nvim")
	Plug 'nvim-treesitter/nvim-treesitter', {'do': ':TSUpdate'}
	Plug 'HiPhish/rainbow-delimiters.nvim'
else
	" Support highlighting for lots of languages
	set re=0 " Disable old regex engine for performance
	Plug 'sheerun/vim-polyglot'
endif


" LaTeX
Plug 'lervag/vimtex'
if has("nvim")
	let g:vimtex_syntax_enabled = 0 "Since neovim uses treesitter
endif
let g:vimtex_fold_enabled=1
let g:vimtex_quickfix_open_on_warning=0
let g:vimtex_view_method='zathura'

"vim tmux seamless navigation.
"Alt + hjkl to move pane/buffer
Plug 'christoomey/vim-tmux-navigator'

let g:tmux_navigator_no_mappings = 1

nnoremap <silent> <M-h> :TmuxNavigateLeft<cr>
nnoremap <silent> <M-j> :TmuxNavigateDown<cr>
nnoremap <silent> <M-k> :TmuxNavigateUp<cr>
nnoremap <silent> <M-l> :TmuxNavigateRight<cr>
nnoremap <silent> <M-\> :TmuxNavigatePrevious<cr>


Plug 'scrooloose/nerdtree'
nmap <C-n> :NERDTreeToggle <CR>

"nerdtree 자동 실행
"autocmd vimenter * NERDTree
autocmd StdinReadPre * let s:std_in=1
"autocmd VimEnter * if argc() == 0 && !exists("s:std_in") | NERDTree | endif
autocmd VimEnter * if argc() == 1 && isdirectory(argv()[0]) && !exists("s:std_in") | exe 'NERDTree' argv()[0] | wincmd p | ene | endif
autocmd bufenter * if (winnr("$") == 1 && exists("b:NERDTree") && b:NERDTree.isTabTree()) | q | endif

Plug 'coot/CRDispatcher'
Plug 'coot/EnchantedVim'
" Since I use incsearch:
set incsearch
let g:VeryMagic = 0
nnoremap / /\v
nnoremap ? ?\v
vnoremap / /\v
vnoremap ? ?\v
" If I type // or ??, I don't EVER want \v, since I'm repeating the previous
" search.
noremap // //
noremap ?? ??
" no-magic searching
noremap /v/ /\V
noremap ?V? ?\V

let g:VeryMagicSubstituteNormalise = 1
let g:VeryMagicSubstitute = 1
let g:VeryMagicGlobal = 1
let g:VeryMagicVimGrep = 1
let g:VeryMagicSearchArg = 1
let g:VeryMagicFunction = 1
let g:VeryMagicHelpgrep = 1
let g:VeryMagicRange = 1
let g:VeryMagicEscapeBackslashesInSearchArg = 1
let g:SortEditArgs = 1

Plug 'vim-test/vim-test'
" Save file before invoking the test
nmap <silent> <leader>t  :write! <bar> TestNearest <CR>
nmap <silent> <leader>T  :write! <bar> TestFile    <CR>

" coc-sh가 .env를 shell script로 인식한다. 이 경우 unused variable로 모든
" 변수를 인식하여 가독성이 떨어지는 문제를 회피하기 위함이다.
autocmd BufNewFile,BufRead .env,.*.env set filetype=env

aug indentation
	autocmd FileType bazel setlocal tabstop=4 softtabstop=4 shiftwidth=4 noexpandtab

	autocmd FileType typescript setlocal tabstop=2 softtabstop=2 shiftwidth=2 expandtab
	autocmd FileType typescriptreact setlocal tabstop=2 softtabstop=2 shiftwidth=2 expandtab
	autocmd FileType javascript setlocal tabstop=2 softtabstop=2 shiftwidth=2 expandtab
	autocmd FileType javascriptreact setlocal tabstop=2 softtabstop=2 shiftwidth=2 expandtab
aug end

aug test_keymap
	autocmd FileType python	nmap <silent> <leader>t  :write! <bar> TestNearest --verbose<CR>
	autocmd FileType python	nmap <silent> <leader>T  :write! <bar> TestFile    --verbose<CR>
aug end

aug vertical_cursor
	autocmd FileType yaml set cursorcolumn
	autocmd FileType python	set cursorcolumn
aug end

let test#strategy = "floaterm"

Plug 'voldikss/vim-floaterm'
let g:floaterm_autoclose = 0
let g:floaterm_width = 1.0
let g:floaterm_height = 0.4
let g:floaterm_wintype = "split"
let g:floaterm_keymap_toggle='<F1>'
tnoremap <ESC> <C-\><C-n>
if has('nvim')
  autocmd TermOpen * setlocal nonumber norelativenumber
endif

" Add maktaba and coverage to the runtimepath.
" (The latter must be installed before it can be used.)
Plug 'google/vim-maktaba'
Plug 'google/vim-coverage'
" Also add Glaive, which is used to configure coverage's maktaba flags. See
" `:help :Glaive` for usage.
Plug 'google/vim-glaive'

Plug 'elixir-lsp/coc-elixir', {'do': 'yarn install && yarn prepack'}

" Markdown renderer
Plug 'iamcco/markdown-preview.nvim', { 'do': 'cd app && npx --yes yarn install' }

" #######################
" ##### neovim only #####
" #######################
if has("nvim")
  let g:loaded_clipboard_provider = 1

  Plug 'folke/twilight.nvim'
  Plug 'f-person/git-blame.nvim'
  let g:gitblame_message_template = '	<author> • <date> • <summary>'
  command! -nargs=0 GBlame :GitBlameToggle
  Plug 'lewis6991/spellsitter.nvim'
  set spell

  " vim의 기본 f 기능을 확장함. 
  " <leader><leader> s + <1char>: 현재 커서 기준으로 앞뒤에있는 <1char>로 점프
  Plug 'smoka7/hop.nvim'
  
  nmap <leader><leader>s :HopChar1<CR>
  xmap <leader><leader>s :HopChar1<CR>
  omap <leader><leader>s :HopChar1<CR>
  nmap f :HopChar1<CR>
  xmap f :HopChar1<CR>
  omap f :HopChar1<CR>
  
  " Sneak 처럼 두 글자를 인식하여 너무 많은 패턴의 경우의 수를 제한한다.
  nmap <leader><leader>S :HopChar2<CR>
  xmap <leader><leader>S :HopChar2<CR>
  omap <leader><leader>S :HopChar2<CR>


  " Claude integration
  Plug 'coder/claudecode.nvim'
  " 키맵핑 설정
  nnoremap <leader>aa <cmd>ClaudeCode<cr>
  vnoremap <leader>ae <cmd>ClaudeCodeSend<cr>
endif


Plug 'skywind3000/asyncrun.vim', {'on': ['AsyncRun', 'AsyncStop'] }
Plug 'skywind3000/asynctasks.vim', {'on': ['AsyncTask', 'AsyncTaskMacro', 'AsyncTaskList', 'AsyncTaskEdit'] }
let g:asynctasks_term_pos = 'bottom'
let g:asyncrun_open = 6
let g:asynctasks_term_focus = 0
let g:asynctasks_term_rows=15

call plug#end()			" required

" Another call must be invoked after `call plug#end()`
call glaive#Install()
" Optional: Enable coverage's default mappings on the <Leader>C prefix.
" <leader>Ct to toggle coverage
Glaive coverage plugin[mappings]

"set theme
"set t_Co=256
"set t_ut= "테마 적용시 뒷 배경을 날리는 역할

" Enable 24bit true color
set termguicolors

" Correct RGB escape codes for vim inside tmux
if !has('nvim') && &term =~ '^\%(screen\|tmux\)'
  " nvim's tree-sitter has a problem that cannot parse the lines below (t_f8, t_8b).
  " Thankfully, adding a comment can prevent this odd error.
  " That's why I added silly comments below.
  let &t_8f = "\<ESC>[38;2;%lu;%lu;%lum"
  " above: foreground color (r, g, b) 
  let &t_8b = "\<ESC>[48;2;%lu;%lu;%lum"
  " above: background color (r, g, b) 
endif

let g:gruvbox_material_enable_bold=1
let g:gruvbox_material_enable_italic=1
let g:gruvbox_material_background='medium' " hard | medium | soft
let g:gruvbox_material_foreground='material' " material | mix | original
let g:gruvbox_material_diagnostic_text_highlight=1

set background=dark
silent! colorscheme zenburned


syntax on
set nocompatible " 오리지날 VI와 호환하지 않음
set hlsearch
set lazyredraw
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

" Disable coc.nvim on diff mode
" https://github.com/neoclide/coc.nvim/issues/1025#issuecomment-766184176
augroup disableCocInDiff
  autocmd!
  autocmd DiffUpdated * let b:coc_enabled=0
augroup END

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

if has("nvim")
lua <<EOF
function PipeRangedSelection()
    local cmd = vim.fn.input("Command: ")
    if cmd == "" then
        return
    end
    local body = vim.fn.GetVisualSelection(vim.fn.visualmode())
    vim.cmd("redraw")
    local fname = os.tmpname()
    local fp = io.open(fname, "w")
    fp:write(body)
    fp:close()

    -- It's like `cmd <tmpfile` and `cat tmpfile | cmd`.
    -- The former does not need a shell extension so I chose the former one.
    vim.cmd("let g:floaterm_autoinsert=0")
    local result = vim.fn.system(cmd .. " <" .. fname)
    local status = vim.v.shell_error
    vim.cmd("FloatermNew " .. cmd .. " <" .. fname)
    if status == 0 and result == "" then
        vim.cmd("FloatermHide")
    end
    vim.cmd("let g:floaterm_autoinsert=1")
    os.remove(fname)
end
EOF

xnoremap <leader>c :<C-u> lua PipeRangedSelection()<CR>

else
	xnoremap <leader>c :<C-u> call PipeRangedSelection()<CR>

	function! PipeRangedSelection()
		let cmd = input("Command: ")
		redraw
		echo system(cmd, GetVisualSelection(visualmode()))
	endfunction
endif


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
"nmap <F9>       <Plug>(coc-codeaction-cursor)
"nmap <ESC>[20~  <Plug>(coc-codeaction-cursor)
nmap <F9>       <Plug>(coc-codeaction-line)
nmap <ESC>[20~  <Plug>(coc-codeaction-line)

" ------------------------------------------------------------------------------
" Press <C-F5> or <F5> to run code
nmap <C-F5>      : AsyncTask fild-build-and-run <CR>
" In some terminals (e.g. tmux), they cannot understand complex key bindings.
" So, in this case, we need to find out the complex binding is converted into
" several keys. 
" For example, if we want to know byte streams of Ctrl + F5, we
" just run xxd in bash, press <Ctrl + F5> and enter.
" Then, 1b5b 3135 3b35 7e0a will be printed. The last 0a is a return key, so
" remaining 7 bytes are what we wanted. The only left thing is, google ascii
" table and translate 7 bytes to '<esc>[15;5~'. 
nmap <ESC>[15;5~ : AsyncTask file-build-and-run <CR>
" In neovim, <C-F5> is mapped to <F29>. To confirm this, try entering <C-F5>
" in insert mode
nmap <F29>       : AsyncTask file-build-and-run <CR>

nmap <F5>        : AsyncTask file-build-and-run <CR>
nmap <ESC>[15~   : AsyncTask file-build-and-run <CR>


" ------------------------------------------------------------------------------
" FIX: ssh from wsl starting with REPLACE mode
" https://stackoverflow.com/a/11940894
if !has("nvim") && $TERM =~ 'xterm-256color'
	set noesckeys
endif

if !has("nvim")
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
endif

if has("patch-8.1.0360") || has("nvim")
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


" Vim

color desert

" Highly recommended to set tab keys to 4 spaces
set shiftwidth=4
set noet
set tabstop=4

" Kill the fricking folds
set nofoldenable
set fdls=99

set autoindent
set autowrite
"
" The opposite is 'set wrapscan' while searching for strings....
set nowrapscan
set number
"
" The opposite is set noignorecase
set ignorecase
" 
" You may want to turn off the beep sounds (if you want quiet) with visual bell
set vb
" Source in your custom filetypes as given below -
" so $HOME/vim/myfiletypes.vim
filetype plugin on
" Make command line two lines high
set ch=2
" Make shift-insert work like in Xterm
map <S-Insert> <MiddleMouse>
map! <S-Insert> <MiddleMouse>
" Only do this for Vim version 5.0 and later.
if version >= 500
  " I like highlighting strings inside C comments
  let c_comment_strings=1

  let python_highlight_builtins=1
  let python_highlight_space_errors=1

  " Switch on syntax highlighting.
  syntax on
  " Switch on search pattern highlighting.
  set hlsearch
  " Hide the mouse pointer while typing
  set mousehide
endif

noremap <C-^> <C-^>`"

map <C-N> :bn!<CR>
map <C-P> :bp!<CR>

" enable terminal/gui mouse use
set mouse=a

" Dos2unix (remove the ^M's)
command DU 1,$s///

set formatoptions=tcq
filetype indent on

set modeline
set nobackup
set nowritebackup

nnoremap \tp :set invpaste paste?<CR>
nmap <F4> \tp
imap <F4> <C-O>\tp
set pastetoggle=<F4>

if hostname() == "shostakovich"
	set guifont=Droid\ Sans\ Mono\ 14
endif

autocmd FileType python set noet

augroup filetypedetect
  au BufRead,BufNewFile COMMIT_EDITMSG setf gitcommit
  au! BufRead,BufNewFile *.nc   setfiletype nc
augroup END
set noet

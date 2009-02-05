augroup filetypedetect
  au BufRead,BufNewFile COMMIT_EDITMSG setf git
  au! BufRead,BufNewFile *.nc   setfiletype nc
augroup END

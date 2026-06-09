-------------------------------
-- Bootstrap lazy.nvim
-------------------------------
local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not (vim.uv or vim.loop).fs_stat(lazypath) then
  vim.fn.system({
    "git", "clone", "--filter=blob:none",
    "https://github.com/folke/lazy.nvim.git",
    "--branch=stable", lazypath,
  })
end
vim.opt.rtp:prepend(lazypath)

-------------------------------
-- Early settings
-------------------------------
vim.g.mapleader = ","
vim.g.loaded_clipboard_provider = 1

-------------------------------
-- Clipboard hook
-------------------------------
vim.cmd("source ~/.clipboard/vimhooks.vim")

-------------------------------
-- Plugins
-------------------------------
require("lazy").setup({
  -- Git
  { "tpope/vim-fugitive" },
  { "tommcdo/vim-fugitive-blame-ext", dependencies = { "tpope/vim-fugitive" } },

  -- Themes
  { "shaunsingh/nord.nvim" },
  { "tomasr/molokai" },
  {
    "sainnhe/gruvbox-material",
    init = function()
      vim.g.gruvbox_material_enable_bold = 1
      vim.g.gruvbox_material_enable_italic = 1
      vim.g.gruvbox_material_background = "medium"
      vim.g.gruvbox_material_foreground = "material"
      vim.g.gruvbox_material_diagnostic_text_highlight = 1
    end,
  },
  { "pineapplegiant/spaceduck", branch = "main" },
  { "NLKNguyen/papercolor-theme" },
  { "danilo-augusto/vim-afterglow" },
  { "vigoux/oak" },
  {
    "mcchrish/zenbones.nvim",
    dependencies = { "rktjmp/lush.nvim" },
    priority = 1000,
    config = function()
      vim.opt.termguicolors = true
      vim.opt.background = "light"
      vim.cmd("silent! colorscheme zenwritten")
    end,
  },

  -- Status line
  {
    "vim-airline/vim-airline",
    dependencies = { "vim-airline/vim-airline-themes" },
    init = function()
      vim.g["airline#extensions#tabline#enabled"] = 1
      vim.g["airline#extensions#tabline#fnamemod"] = ":t"
      vim.g["airline#extensions#tabline#buffer_nr_show"] = 1
      vim.g["airline#extensions#tabline#buffer_nr_format"] = "%s:"
      vim.opt.laststatus = 2
      vim.g["airline#extensions#whitespace#enabled"] = 0
      vim.g.airline_theme = "tomorrow"
      vim.g.airline_powerline_fonts = 1
      if vim.fn.exists("g:airline_symbols") == 0 then
        vim.g.airline_symbols = vim.empty_dict()
      end
    end,
  },

  -- LSP (coc.nvim)
  {
    "neoclide/coc.nvim",
    branch = "release",
    init = function()
      vim.cmd("silent! source ~/.coc.vimrc")
      vim.g.coc_global_extensions = {
        "coc-biome",
        "coc-calc",
        "coc-clangd",
        "coc-cmake",
        "coc-elixir",
        "coc-floaterm",
        "coc-git",
        "coc-go",
        "coc-java",
        "coc-json",
        "coc-markdownlint",
        "coc-pairs",
        "coc-perl",
        "coc-pyright",
        "coc-rust-analyzer",
        "coc-sh",
        "coc-snippets",
        "coc-sql",
        "coc-sumneko-lua",
        "coc-terminal",
        "coc-toml",
        "coc-tsserver",
        "coc-vimlsp",
        "coc-vimtex",
        "coc-xml",
        "coc-yaml",
        "https://github.com/cstrap/python-snippets",
        "https://github.com/rafamadriz/friendly-snippets@main",
      }
    end,
  },
  { "elixir-lsp/coc-elixir", build = "yarn install && yarn prepack" },

  -- Tmux airline
  {
    "edkolev/tmuxline.vim",
    init = function()
      vim.g["airline#extensions#tmuxline#enabled"] = 0
    end,
  },

  -- Git graph
  { "rbong/vim-flog", dependencies = { "tpope/vim-fugitive" } },

  -- Indent guides
  {
    "Yggdroot/indentLine",
    init = function()
      vim.g.indentLine_setConceal = 0
      vim.g.indentLine_char = "┊"
      vim.opt.list = true
      vim.opt.listchars = { tab = "┊ " }
    end,
  },

  -- fzf
  {
    "junegunn/fzf.vim",
    dependencies = { "junegunn/fzf" },
    config = function()
      vim.keymap.set("n", "<leader><C-n>", ":Files<CR>")
      if vim.fn.executable("rg") == 1 then
        vim.keymap.set("n", "<leader>r", ":Rg!<CR>")
      else
        vim.keymap.set("n", "<leader>r", ":Ag!<CR>")
      end
      vim.cmd([[
        command! -bang -nargs=* Ag call fzf#vim#ag(<q-args>, {'options': '--delimiter : --nth 4..'}, <bang>0)
        command! -bang -nargs=* Rg
          \ call fzf#vim#grep("rg --column --line-number --no-heading --color=always --smart-case ".shellescape(<q-args>), 1,
          \   fzf#vim#with_preview({'options': '--delimiter : --nth 4..'}), <bang>0)
      ]])
    end,
  },

  -- Folding
  {
    "kevinhwang91/nvim-ufo",
    dependencies = { "kevinhwang91/promise-async" },
    config = function()
      vim.o.foldlevel = 20
      vim.o.foldenable = true

      local function chainedSelector(bufnr)
        local function handleFallbackException(err, providerName)
          if type(err) == "string" and err:match("UfoFallbackException") then
            return require("ufo").getFolds(bufnr, providerName)
          else
            return require("promise").reject(err)
          end
        end
        return require("ufo").getFolds(bufnr, "lsp"):catch(function(err)
          return handleFallbackException(err, "treesitter")
        end):catch(function(err)
          return handleFallbackException(err, "indent")
        end)
      end

      local function peekOrHover()
        local winid = require("ufo").peekFoldedLinesUnderCursor()
        if not winid then
          vim.fn.CocActionAsync("definitionHover")
        end
      end

      local function applyFoldsAndThenCloseAllFolds(bufnr, providerName)
        return require("async")(function()
          bufnr = bufnr or vim.api.nvim_get_current_buf()
          require("ufo").attach(bufnr)
          local ranges = await(require("ufo").getFolds(bufnr, providerName))
          local ok = require("ufo").applyFolds(bufnr, ranges)
          if ok then
            require("ufo").closeAllFolds()
          end
        end)
      end

      require("ufo").setup({
        preview = {
          mappings = {
            scrollU = "<C-u>",
            scrollD = "<C-d>",
          },
        },
        provider_selector = function(bufnr, filetype, buftype)
          return chainedSelector
        end,
      })

      vim.keymap.set("n", "zR", require("ufo").openAllFolds)
      vim.keymap.set("n", "zM", require("ufo").closeAllFolds)
      vim.keymap.set("n", "zr", "ggvGzo<C-o>zz")
      vim.keymap.set("n", "zm", require("ufo").closeFoldsWith, {})
      vim.keymap.set("n", "K", peekOrHover)

      vim.api.nvim_create_autocmd("BufRead", {
        pattern = "*",
        callback = function(e)
          applyFoldsAndThenCloseAllFolds(e.buf, "treesitter"):catch(function()
            applyFoldsAndThenCloseAllFolds(e.buf, "indent")
          end)
        end,
      })
    end,
  },

  -- Treesitter
  {
    "nvim-treesitter/nvim-treesitter",
    branch = "main",
    build = ":TSUpdate",
    config = function()
      local ts_parsers = {
        "bash", "bibtex", "c", "cmake", "comment", "cpp", "css",
        "dockerfile", "elixir", "erlang", "git_config", "git_rebase",
        "gitattributes", "gitcommit", "gitignore", "go", "gomod",
        "graphql", "html", "java", "javascript", "jsdoc", "json",
        "json5", "kotlin", "latex", "lua", "luadoc", "make",
        "markdown", "markdown_inline", "passwd", "perl", "php",
        "python", "racket", "regex", "rust", "scheme", "scss",
        "sql", "toml", "tsx", "typescript", "vim", "vimdoc", "yaml",
      }
      pcall(function()
        require("nvim-treesitter").install(ts_parsers)
      end)
      vim.api.nvim_create_autocmd("FileType", {
        pattern = "*",
        callback = function(args)
          pcall(vim.treesitter.start, args.buf)
        end,
      })
      vim.api.nvim_create_autocmd("FileType", {
        pattern = { "elixir", "sql" },
        callback = function()
          vim.bo.indentexpr = "v:lua.require'nvim-treesitter'.indentexpr()"
        end,
      })
    end,
  },

  -- Rainbow delimiters
  {
    "HiPhish/rainbow-delimiters.nvim",
    config = function()
      require("rainbow-delimiters.setup").setup({
        query = {
          [""] = "rainbow-delimiters",
          lua = "rainbow-blocks",
          latex = "rainbow-blocks",
        },
      })
    end,
  },

  -- LaTeX
  {
    "lervag/vimtex",
    init = function()
      vim.g.vimtex_syntax_enabled = 0
      vim.g.vimtex_fold_enabled = 1
      vim.g.vimtex_quickfix_open_on_warning = 0
      vim.g.vimtex_view_method = "zathura"
    end,
  },

  -- Tmux navigation
  {
    "christoomey/vim-tmux-navigator",
    init = function()
      vim.g.tmux_navigator_no_mappings = 1
    end,
    config = function()
      vim.keymap.set("n", "<M-h>", ":TmuxNavigateLeft<CR>", { silent = true })
      vim.keymap.set("n", "<M-j>", ":TmuxNavigateDown<CR>", { silent = true })
      vim.keymap.set("n", "<M-k>", ":TmuxNavigateUp<CR>", { silent = true })
      vim.keymap.set("n", "<M-l>", ":TmuxNavigateRight<CR>", { silent = true })
      vim.keymap.set("n", "<M-\\>", ":TmuxNavigatePrevious<CR>", { silent = true })
    end,
  },

  -- File tree
  {
    "scrooloose/nerdtree",
    config = function()
      vim.keymap.set("n", "<C-n>", ":NERDTreeToggle<CR>")
      vim.cmd([[
        autocmd StdinReadPre * let s:std_in=1
        autocmd VimEnter * if argc() == 1 && isdirectory(argv()[0]) && !exists("s:std_in") | exe 'NERDTree' argv()[0] | wincmd p | ene | endif
        autocmd bufenter * if (winnr("$") == 1 && exists("b:NERDTree") && b:NERDTree.isTabTree()) | q | endif
      ]])
    end,
  },

  -- Enhanced search (very magic)
  {
    "coot/EnchantedVim",
    dependencies = { "coot/CRDispatcher" },
    init = function()
      vim.g.VeryMagic = 0
      vim.g.VeryMagicSubstituteNormalise = 1
      vim.g.VeryMagicSubstitute = 1
      vim.g.VeryMagicGlobal = 1
      vim.g.VeryMagicVimGrep = 1
      vim.g.VeryMagicSearchArg = 1
      vim.g.VeryMagicFunction = 1
      vim.g.VeryMagicHelpgrep = 1
      vim.g.VeryMagicRange = 1
      vim.g.VeryMagicEscapeBackslashesInSearchArg = 1
      vim.g.SortEditArgs = 1
    end,
    config = function()
      vim.keymap.set("n", "/", "/\\v")
      vim.keymap.set("n", "?", "?\\v")
      vim.keymap.set("v", "/", "/\\v")
      vim.keymap.set("v", "?", "?\\v")
      vim.keymap.set("", "//", "//")
      vim.keymap.set("", "??", "??")
      vim.keymap.set("", "/v/", "/\\V")
      vim.keymap.set("", "?V?", "?\\V")
    end,
  },

  -- Test runner
  {
    "vim-test/vim-test",
    init = function()
      vim.g["test#strategy"] = "floaterm"
    end,
    config = function()
      vim.keymap.set("n", "<leader>t", ":write! <bar> TestNearest<CR>", { silent = true })
      vim.keymap.set("n", "<leader>T", ":write! <bar> TestFile<CR>", { silent = true })
    end,
  },

  -- Floating terminal
  {
    "voldikss/vim-floaterm",
    init = function()
      vim.g.floaterm_autoclose = 0
      vim.g.floaterm_width = 1.0
      vim.g.floaterm_height = 0.4
      vim.g.floaterm_wintype = "split"
      vim.g.floaterm_keymap_toggle = "<F1>"
    end,
  },

  -- Code coverage
  {
    "google/vim-coverage",
    dependencies = { "google/vim-maktaba", "google/vim-glaive" },
    config = function()
      vim.cmd([[
        call glaive#Install()
        Glaive coverage plugin[mappings]
      ]])
    end,
  },

  -- Markdown preview
  { "iamcco/markdown-preview.nvim", build = "cd app && npx --yes yarn install" },

  -- Focus mode
  { "folke/twilight.nvim" },

  -- Git blame
  {
    "f-person/git-blame.nvim",
    init = function()
      vim.g.gitblame_message_template = "\t<author> • <date> • <summary>"
    end,
    config = function()
      vim.api.nvim_create_user_command("GBlame", "GitBlameToggle", {})
    end,
  },


  -- Easy motion
  {
    "smoka7/hop.nvim",
    config = function()
      require("hop").setup({ case_insensitive = false })
      vim.keymap.set("n", "<leader><leader>s", ":HopChar1<CR>")
      vim.keymap.set("x", "<leader><leader>s", ":HopChar1<CR>")
      vim.keymap.set("o", "<leader><leader>s", ":HopChar1<CR>")
      vim.keymap.set("n", "f", ":HopChar1<CR>")
      vim.keymap.set("x", "f", ":HopChar1<CR>")
      vim.keymap.set("o", "f", ":HopChar1<CR>")
      vim.keymap.set("n", "<leader><leader>S", ":HopChar2<CR>")
      vim.keymap.set("x", "<leader><leader>S", ":HopChar2<CR>")
      vim.keymap.set("o", "<leader><leader>S", ":HopChar2<CR>")
    end,
  },

  -- Claude integration
  {
    "coder/claudecode.nvim",
    config = function()
      require("claudecode").setup({
        terminal = { provider = "native" },
      })
      vim.keymap.set("n", "<leader>aa", "<cmd>ClaudeCode<cr>")
      vim.keymap.set("v", "<leader>ae", "<cmd>ClaudeCodeSend<cr>")
    end,
  },

  -- Async tasks
  { "skywind3000/asyncrun.vim", cmd = { "AsyncRun", "AsyncStop" } },
  {
    "skywind3000/asynctasks.vim",
    dependencies = { "skywind3000/asyncrun.vim" },
    cmd = { "AsyncTask", "AsyncTaskMacro", "AsyncTaskList", "AsyncTaskEdit" },
    init = function()
      vim.g.asynctasks_term_pos = "bottom"
      vim.g.asyncrun_open = 6
      vim.g.asynctasks_term_focus = 0
      vim.g.asynctasks_term_rows = 15
    end,
  },
})

-------------------------------
-- Options
-------------------------------
vim.cmd("syntax on")
vim.opt.compatible = false
vim.opt.hlsearch = true
vim.opt.incsearch = true
vim.opt.lazyredraw = true
vim.opt.ignorecase = true
vim.opt.smartcase = true
vim.opt.autoindent = true
vim.opt.cindent = true
vim.opt.smartindent = true
vim.opt.wrap = true
vim.opt.linebreak = true
vim.opt.wrapscan = false
vim.opt.backup = false
vim.opt.swapfile = false
vim.opt.visualbell = true
vim.opt.belloff:append("esc")
vim.opt.ruler = true
vim.opt.shiftwidth = 4
vim.opt.tabstop = 4
vim.opt.number = true
vim.opt.fileencodings = "ucs-bom,utf-8,cp949,euc-kr"
vim.opt.conceallevel = 2
vim.opt.concealcursor = ""
vim.opt.signcolumn = "auto"
vim.opt.guicursor = ""
vim.opt.mouse = ""
vim.opt.spell = true
vim.opt.spelllang = "en,cjk"
vim.opt.spellsuggest = "best,9"
vim.opt.autoread = true

vim.opt.diffopt:append("iwhite")
vim.opt.diffopt:append("vertical")
vim.opt.diffopt:append("filler")
vim.opt.diffopt:append("internal,algorithm:histogram")
vim.opt.diffopt:append("indent-heuristic")

-------------------------------
-- Keymaps
-------------------------------
vim.keymap.set("n", "n", "nzz")
vim.keymap.set("n", "N", "Nzz")
vim.keymap.set("n", "<leader>q", ":bp!<CR>")
vim.keymap.set("n", "<leader>w", ":bn!<CR>")
vim.keymap.set("n", "<leader>d", ":bp <BAR> bd #<CR>")
vim.keymap.set("n", "<leader>e", "<C-W>w")
vim.keymap.set("t", "<ESC>", "<C-\\><C-n>")

-- coc code actions
vim.keymap.set("n", "<F9>", "<Plug>(coc-codeaction-line)")
vim.keymap.set("n", "<ESC>[20~", "<Plug>(coc-codeaction-line)")

-- AsyncTask
vim.keymap.set("n", "<C-F5>", ":AsyncTask file-build-and-run<CR>")
vim.keymap.set("n", "<ESC>[15;5~", ":AsyncTask file-build-and-run<CR>")
vim.keymap.set("n", "<F29>", ":AsyncTask file-build-and-run<CR>")
vim.keymap.set("n", "<F5>", ":AsyncTask file-build-and-run<CR>")
vim.keymap.set("n", "<ESC>[15~", ":AsyncTask file-build-and-run<CR>")

-------------------------------
-- Autocmds
-------------------------------
vim.api.nvim_create_autocmd({ "BufNewFile", "BufRead" }, {
  pattern = { ".env", ".*.env" },
  callback = function() vim.bo.filetype = "env" end,
})

vim.api.nvim_create_autocmd("FileType", {
  pattern = { "typescript", "typescriptreact", "javascript", "javascriptreact" },
  callback = function()
    vim.bo.tabstop = 2
    vim.bo.softtabstop = 2
    vim.bo.shiftwidth = 2
    vim.bo.expandtab = true
  end,
})

vim.api.nvim_create_autocmd("FileType", {
  pattern = "bazel",
  callback = function()
    vim.bo.tabstop = 4
    vim.bo.softtabstop = 4
    vim.bo.shiftwidth = 4
    vim.bo.expandtab = false
  end,
})

vim.api.nvim_create_autocmd("FileType", {
  pattern = "elixir",
  callback = function()
    vim.bo.tabstop = 2
    vim.bo.softtabstop = 2
    vim.bo.shiftwidth = 2
    vim.bo.expandtab = true
  end,
})

vim.api.nvim_create_autocmd("FileType", {
  pattern = "python",
  callback = function()
    vim.keymap.set("n", "<leader>t", ":write! <bar> TestNearest --verbose<CR>", { buffer = true, silent = true })
    vim.keymap.set("n", "<leader>T", ":write! <bar> TestFile --verbose<CR>", { buffer = true, silent = true })
    vim.opt_local.cursorcolumn = true
  end,
})

vim.api.nvim_create_autocmd("FileType", {
  pattern = "yaml",
  callback = function() vim.opt_local.cursorcolumn = true end,
})

vim.api.nvim_create_autocmd("FileType", {
  pattern = "tex",
  callback = function() vim.opt_local.spell = true end,
})

vim.api.nvim_create_autocmd("TermOpen", {
  callback = function()
    vim.opt_local.number = false
    vim.opt_local.relativenumber = false
  end,
})

vim.api.nvim_create_autocmd("CursorHold", {
  callback = function() vim.cmd("checktime") end,
})

-- Disable coc.nvim on diff mode
vim.api.nvim_create_autocmd("DiffUpdated", {
  callback = function() vim.b.coc_enabled = 0 end,
})

-- Filetype for custom extensions
vim.api.nvim_create_autocmd("BufEnter", {
  pattern = { "*.shrc", "*.shinit" },
  callback = function() vim.bo.filetype = "sh" end,
})
vim.api.nvim_create_autocmd("BufEnter", {
  pattern = "*.nsp",
  callback = function() vim.bo.filetype = "json" end,
})
vim.api.nvim_create_autocmd("BufEnter", {
  pattern = "coc-settings.json",
  callback = function() vim.bo.filetype = "jsonc" end,
})

-- Restore last edit position
vim.api.nvim_create_autocmd("BufReadPost", {
  callback = function()
    local mark = vim.api.nvim_buf_get_mark(0, '"')
    local lcount = vim.api.nvim_buf_line_count(0)
    if mark[1] > 0 and mark[1] <= lcount then
      pcall(vim.api.nvim_win_set_cursor, 0, mark)
    end
  end,
})

-- Auto-convert dos line endings and legacy encodings
vim.api.nvim_create_autocmd("BufReadPost", {
  callback = function()
    if not vim.bo.modifiable then return end
    if vim.tbl_contains({ "dosbatch", "ps1" }, vim.bo.filetype) then return end
    if vim.bo.fileformat ~= "unix" then
      vim.bo.fileformat = "unix"
      vim.cmd([[silent! %s/\r//ge]])
      vim.cmd("silent write")
    end
    local fenc = vim.bo.fileencoding
    if fenc == "euc-kr" or fenc == "cp949" then
      vim.bo.fileencoding = "utf-8"
      vim.cmd("silent write")
    end
  end,
})

-- Modifiable state matches readonly state
vim.api.nvim_create_autocmd("BufReadPost", {
  callback = function()
    if vim.b.setmodifiable == nil then
      vim.b.setmodifiable = 0
    end
    if vim.bo.readonly then
      if vim.bo.modifiable then
        vim.bo.modifiable = false
        vim.b.setmodifiable = 1
      end
    else
      if vim.b.setmodifiable == 1 then
        vim.bo.modifiable = true
      end
    end
  end,
})

-- Vimdiff: ignore readonly
if vim.opt.diff:get() then
  vim.opt.readonly = false
end

-------------------------------
-- Utility functions
-------------------------------
vim.cmd([[
function! GetVisualSelection(mode)
  let [line_start, column_start] = getpos("'<")[1:2]
  let [line_end, column_end]     = getpos("'>")[1:2]
  let lines = getline(line_start, line_end)
  if a:mode ==# 'v'
    let lines[-1] = lines[-1][: column_end - (&selection == 'inclusive' ? 1 : 2)]
    let lines[0] = lines[0][column_start - 1:]
  elseif  a:mode ==# 'V'
  elseif  a:mode == "\<c-v>"
    let new_lines = []
    let i = 0
    for line in lines
      let lines[i] = line[column_start - 1: column_end - (&selection == 'inclusive' ? 1 : 2)]
      let i = i + 1
    endfor
  else
    return ''
  endif
  return join(lines, "\n")
endfunction
]])

function PipeRangedSelection()
  local cmd = vim.fn.input("Command: ")
  if cmd == "" then return end
  local body = vim.fn.GetVisualSelection(vim.fn.visualmode())
  vim.cmd("redraw")
  local fname = os.tmpname()
  local fp = io.open(fname, "w")
  fp:write(body)
  fp:close()

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

vim.keymap.set("x", "<leader>c", ":<C-u> lua PipeRangedSelection()<CR>")

-------------------------------
-- Python host
-------------------------------
vim.g.python3_host_prog = vim.fn.expand("~/.local/share/nvim/python3-host/bin/python")

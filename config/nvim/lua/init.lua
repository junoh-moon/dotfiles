-----------
-- nvim-ufo
-----------
vim.o.foldlevel = 20 -- Using ufo provider need a large value, feel free to decrease the value
vim.o.foldenable = true

-- lsp or else treesitter or else indent
local function chainedSelector(bufnr)
	local function handleFallbackException(err, providerName)
		if type(err) == 'string' and err:match('UfoFallbackException') then
			return require('ufo').getFolds(bufnr, providerName)
		else
			return require('promise').reject(err)
		end
	end

	return require('ufo').getFolds(bufnr, 'lsp'):catch(function(err)
		return handleFallbackException(err, 'treesitter')
	end):catch(function(err)
		return handleFallbackException(err, 'indent')
	end)
end

local function peekOrHover()
	local winid = require('ufo').peekFoldedLinesUnderCursor()
	if not winid then
		vim.fn.CocActionAsync('definitionHover') -- coc.nvim
	end
end

local function applyFoldsAndThenCloseAllFolds(bufnr, providerName)
	return require('async')(function()
		bufnr = bufnr or vim.api.nvim_get_current_buf()
		-- make sure buffer is attached
		require('ufo').attach(bufnr)
		-- getFolds return Promise if providerName == 'lsp'
		local ranges = await(require('ufo').getFolds(bufnr, providerName))
		local ok = require('ufo').applyFolds(bufnr, ranges)
		if ok then
			require('ufo').closeAllFolds()
		end
	end)
end

require('ufo').setup({
	preview = {
		mappings = {
			scrollU = '<C-u>',
			scrollD = '<C-d>',
		},
	},
	provider_selector = function(bufnr, filetype, buftype)
		return chainedSelector
	end
})

-- Using ufo provider need remap `zR` and `zM`. If Neovim is 0.6.1, remap yourself
vim.keymap.set('n', 'zR', require('ufo').openAllFolds)
vim.keymap.set('n', 'zM', require('ufo').closeAllFolds)
vim.keymap.set('n', 'zr', 'ggvGzo<C-o>zz')                   -- Open folding by one level, go back cursor, and let the cursor on the middle.
vim.keymap.set('n', 'zm', require('ufo').closeFoldsWith, {}) -- Usage: zm, 1zm, 2zm, ...
vim.keymap.set('n', 'K', peekOrHover)


-- Fold code on startup
vim.api.nvim_create_autocmd('BufRead', {
	pattern = '*',
	-- Try treesitter first, indent later
	callback = function(e)
		applyFoldsAndThenCloseAllFolds(e.buf, 'treesitter'):catch(function()
			applyFoldsAndThenCloseAllFolds(e.buf, 'indent')
		end)
	end
})

------------------
-- claude code
------------------
require('claudecode').setup({
	config = true,
	terminal = {
		provider = "native",
	}
})

------------------
-- nvim-treesitter
------------------
require("nvim-treesitter.configs").setup {
	ensure_installed = {
		"bash",
		"bibtex",
		"c",
		"cmake",
		"comment",
		"cpp",
		"css",
		"dockerfile",
		"elixir",
		"erlang",
		"git_config",
		"git_rebase",
		"gitattributes",
		"gitcommit",
		"gitignore",
		"go",
		"gomod",
		"graphql",
		"html",
		"java",
		"javascript",
		"jsdoc",
		"json",
		"json5",
		"jsonc",
		"kotlin",
		"latex",
		"lua",
		"luadoc",
		"make",
		"markdown",
		"markdown_inline",
		"passwd",
		"perl",
		"php",
		"python",
		"racket",
		"regex",
		"rust",
		"scheme",
		"scss",
		"sql",
		"toml",
		"tsx",
		"typescript",
		"vim",
		"vimdoc",
		"yaml",
	},
	highlight = {
		enable = true, -- false will disable the whole extension
		additional_vim_regex_highlighting = false,
	},
	indent = {
		enable = true,
		disable = {
			"bash",
			"bibtex",
			"c",
			"cmake",
			"comment",
			"cpp",
			"css",
			"dockerfile",
			"erlang",
			"go",
			"gomod",
			"graphql",
			"html",
			"java",
			"javascript",
			"jsdoc",
			"json",
			"json5",
			"jsonc",
			"kotlin",
			"latex",
			"lua",
			"make",
			"perl",
			"php",
			"python",
			"regex",
			"rust",
			"scss",
			"starlark",
			"toml",
			"tsx",
			"typescript",
			"vim",
			"yaml",
		}
	},
}

require('rainbow-delimiters.setup').setup {
	query = {
		-- Use parentheses by default
		[''] = 'rainbow-delimiters',
		-- Use blocks for Lua
		lua = 'rainbow-blocks',
		latex = 'rainbow-blocks',
	},
}

-----------------------------
-- hop.nvim (easymotion)
-----------------------------
require('hop').setup({
	case_insensitive = false,
})

-----------------------------
-- Avoid yelling about pynvim
-----------------------------
if vim.fn.exists("$VIRTUAL_ENV") == 1 then
	vim.g.python3_host_prog = vim.fn.substitute(vim.fn.system("which -a python3 | head -n2 | tail -n1"), "\n", "", "g")
else
	vim.g.python3_host_prog = vim.fn.substitute(vim.fn.system("which python3"), "\n", "", "g")
end


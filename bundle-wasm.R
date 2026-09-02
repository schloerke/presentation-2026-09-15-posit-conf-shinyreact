# Post-render: hand shinylive the Wasm packages that aren't in its bundled
# library image, so the deck never talks to repo.r-wasm.org at runtime.
#
# shinylive's own bundler (SHINYLIVE_WASM_PACKAGES) can't do this for us: it
# sees `shinyreact` installed from a GitHub remote and demands a GitHub release
# carrying Wasm assets, which posit-dev/shinyreact doesn't have. See CLAUDE.md.
# So we write `packages/metadata.rds` ourselves - the same format the runtime's
# `.mount_vfs_images()` reads, before it looks anything up in a repo.
#
# Everything else the apps need (shiny, bslib, htmltools, cli, jsonlite,
# rlang, ...) is already inside shinylive's `webr/library.data.gz`.

repo <- "wasm-repo/bin/emscripten/contrib/4.5"
pkgs <- c("shinyreact", "brio") # brio: the one shinyreact Import not in the image

webr_dir <- Sys.glob(file.path(
  Sys.getenv("QUARTO_PROJECT_OUTPUT_DIR", "."),
  "*_files/libs/quarto-contrib/shinylive-*/shinylive/webr"
))
if (length(webr_dir) != 1) {
  stop("expected exactly one shinylive webr asset dir, found: ", length(webr_dir))
}

pkg_dir <- file.path(webr_dir, "packages")
dir.create(pkg_dir, recursive = TRUE, showWarnings = FALSE)

metadata <- lapply(pkgs, function(pkg) {
  tgz <- Sys.glob(file.path(repo, paste0(pkg, "_*.tgz")))
  if (length(tgz) != 1) {
    stop("expected exactly one ", pkg, " .tgz in ", repo, ", found: ", length(tgz))
  }
  file <- basename(tgz)
  version <- sub("\\.tgz$", "", sub(paste0("^", pkg, "_"), "", file))

  dir.create(file.path(pkg_dir, pkg), showWarnings = FALSE)
  file.copy(tgz, file.path(pkg_dir, pkg, file), overwrite = TRUE)

  # `path` is relative: the runtime resolves it against webR's asset dir, which
  # is this directory. `type: package` keeps it out of .libPaths() juggling -
  # /shinylive/webr/packages is already on the path.
  list(
    name = pkg,
    version = version,
    ref = paste0(pkg, "@", version),
    type = "package",
    cached = TRUE,
    path = file.path("packages", pkg, file),
    assets = list(list(filename = file, url = "", version = version))
  )
})
names(metadata) <- pkgs

saveRDS(metadata, file.path(pkg_dir, "metadata.rds"))
message("bundle-wasm.R: bundled ", paste(pkgs, collapse = ", "), " into ", pkg_dir)

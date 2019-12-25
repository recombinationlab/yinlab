htmls <- list.files(pattern = "^[A-Za-z].*.html")
files <- list.files(path = "files/")

con = file("sitemap.txt", "w")
writeLines(paste0("https://recombination.dev/", htmls), con = con)
writeLines(paste0("https://recombination.dev/files/", files), con = con)
close(con)

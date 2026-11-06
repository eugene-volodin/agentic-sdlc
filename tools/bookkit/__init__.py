"""bookkit: builds an illustrated A4 handbook from Markdown chapters.

    design      tokens: every color, font and page measurement
    markup      the syntax added to Markdown (":::" blocks, options, front matter)
    markdown    Markdown rendering with book typography
    components  the library of visual blocks
    compiler    chapters -> rows
    pages       cover, contents, openers, the final HTML document
    render      browser: pagination, footer scenes, PDF and PNG output
    proofs      overview sheets of characters, doodles and colors
    cli         the `book` command
    config      book.yml and the locale
    art         the drawings: characters, scenery, doodles, scenes
    theme       style sheets, the paginator, bundled fonts
    locale      the strings the engine prints on pages
"""

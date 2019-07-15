\LoadClass{book}
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{diary}[2019/05/30 My custom diary class]
\RequirePackage{titlesec}
\usepackage{tocloft}
\usepackage{hyperref}
\usepackage{float}
\usepackage[parfill]{parskip}
\usepackage[utf8]{inputenc}
\usepackage{palatino}

\hypersetup{
colorlinks=true,
linkcolor=blue,
filecolor=blue,
urlcolor=blue,
}

\usepackage[margin=1.2in]{geometry}

\urlstyle{same}
\pagestyle{empty}

\setcounter{tocdepth}{4}
\setcounter{secnumdepth}{3}

\setlength{\cftchapindent}{0pt}% Remove indent for \section
\setlength{\cftsecindent}{0pt}% Remove indent for \section
\setlength{\cftsubsecindent}{0pt}% Remove indent for \subsection
\setlength{\cftsubsubsecindent}{0pt}% Remove indent for \section
\addtolength{\cftsubsubsecnumwidth}{20pt}


\titleformat{\subsubsection}         % Customise the \section command
{\large\scshape\raggedright} % Make the \section headers large (\Large),
% small capitals (\scshape) and left aligned (\raggedright)
{}{0em}                      % Can be used to give a prefix to all sections, like 'Section ...'
{}                           % Can be used to insert code before the heading
[\titlerule]                 % Inserts a horizontal line after the heading


\newcommand{\doubledatedsection}[4]{%
\setcounter{chapter}{#1}
\setcounter{section}{#2}
\setcounter{subsection}{#3}
\subsubsection[#4]{#1.#2.#3 \enspace #4}%
}

\newcommand{\doubledatedsectionupdate}[7]{%
\begin{samepage}
\setcounter{chapter}{#1}
\setcounter{section}{#2}
\setcounter{subsection}{#3}
\subsubsection[#7]{#1.#2.#3 \enspace #7}
\begin{flushright} Updated: #4.#5.#6 \end{flushright}
\end{samepage}
}

\newcommand{\makeTagFooter}{
\vspace{5mm}
\noindent \rule{0.2\textwidth}{0.4pt}
\newline
}

\newcommand{\urlorhyperlink}[2]{
\ifx&#2&
    \url{#1}
\else
    \href{#1}{#2}
\fi
}

\newcommand{\makeTitlePage}[3]{
\begin{titlepage} % Suppresses headers and footers on the title page

    \centering % Centre everything on the title page

    \scshape % Use small caps for all text on the title page

    \vspace*{\baselineskip} % White space at the top of the page

    %------------------------------------------------
    %	Title
    %------------------------------------------------

    \rule{\textwidth}{1.6pt}\vspace*{-\baselineskip}\vspace*{2pt} % Thick horizontal rule
    \rule{\textwidth}{0.4pt} % Thin horizontal rule

    \vspace{0.75\baselineskip} % Whitespace above the title

    {Journal: {#1}} % Title

    \vspace{0.75\baselineskip} % Whitespace below the title

    \rule{\textwidth}{0.4pt}\vspace*{-\baselineskip}\vspace{3.2pt} % Thin horizontal rule
    \rule{\textwidth}{1.6pt} % Thick horizontal rule

    \vspace{2\baselineskip} % Whitespace after the title block

    %------------------------------------------------
    %	Subtitle
    %------------------------------------------------

    {#2} - {#3}

    \vspace*{3\baselineskip} % Whitespace under the subtitle

\end{titlepage}

\shipout\null

\pagenumbering{arabic}% Arabic page numbers (and reset to 1)
}


\begin{verbatim}
    def outtextf(self, s):
        self.outtextlist.append(s)
        if s:
            self.lastWasNL = s[-1] == "\n"
\end{verbatim}

Ensure that HTML that starts with a crowded \texttt{<pre>} is converted to
reasonable Markdown.


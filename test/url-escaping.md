{\Huge Markdown-sensible characters processing}

This test checks special characters processing inside URLs: parenthesis and
brackets should be escaped to keep markdown image and anchor syntax safe and
sound.

\begin{itemize}
\item \urlorhyperlink{http://msdn.microsoft.com/en-us/library/system.drawing.drawing2d(v=vs.110)}{Some MSDN link using parenthesis}
\item \urlorhyperlink{https://www.google.ru/search?q=[brackets are cool]}{Google search result URL with unescaped brackets}
\item \urlorhyperlink{https://www.google.ru/search?q='[({})]'}{Yet another test for [brackets], {curly braces} and (parenthesis) processing inside the anchor}
\item Use automatic links like \urlorhyperlink{http://example.com/}{http://example.com/} when the URL is the label
\item Exempt \urlorhyperlink{non-absolute_URIs}{non-absolute_URIs} from automatic link detection
\end{itemize}

And here are images with tricky attribute values:

\begin{figure}[H]\includegraphics[width=\linewidth]{http://placehold.it/350x150#(banana)}\caption{(banana)}\end{figure}\par
\begin{figure}[H]\includegraphics[width=\linewidth]{http://placehold.it/350x150#[banana]}\caption{[banana]}\end{figure}\par
\begin{figure}[H]\includegraphics[width=\linewidth]{http://placehold.it/350x150#{banana}}\caption{{banana}}\end{figure}\par
\begin{figure}[H]\includegraphics[width=\linewidth]{http://placehold.it/350x150#([{}])}\caption{([{}])}\end{figure}
\begin{figure}[H]\includegraphics[width=\linewidth]{http://placehold.it/350x150#([{}])}\end{figure}



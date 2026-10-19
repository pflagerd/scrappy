prototype="prototype"
if [[ -n "$1" ]]; then
    prototype="$1"
fi

printf "        <article style=\"display:none;\" class=\"post\" id=\"%s\"> <!-- %s -->\n" `utcnow` "$prototype"
printf "          <h3>%s</h3>\n" "$prototype"
printf "          <p class=\"meta\">%s by Daniel</p>\n" "$(date)"
printf "          <p>Replace and add to this line some content</p>\n"
printf "        </article> <!-- %s -->\n" "$prototype"

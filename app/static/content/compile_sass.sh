sass scss/custom.scss:./bootstrap.min.css --style=compressed
postcss ./bootstrap.min.css --replace --use autoprefixer
read -p "Press ENTER"

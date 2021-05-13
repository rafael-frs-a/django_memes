document.getElementById('meme_file').onchange = () => {
    let reader = new FileReader();

    reader.onload = (e) => {
        document.getElementById('preview').src = e.target.result;
    };

    reader.readAsDataURL(this.meme_file.files[0]);
};

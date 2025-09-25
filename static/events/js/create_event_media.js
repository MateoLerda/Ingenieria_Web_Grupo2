document.addEventListener('DOMContentLoaded', function(){
  const input = document.getElementById('mediaInput');
  const thumbs = document.getElementById('thumbs');
  if (!input || !thumbs) return;

  let selectedFiles = [];
  let idCounter = 0;

  function syncInputFiles(){
    const dt = new DataTransfer();
    selectedFiles.forEach(item => dt.items.add(item.file));
    input.files = dt.files;
  }

  function addFile(file){
    if (!file || !file.type || !file.type.startsWith('image/')) return;
    const id = `img_${Date.now()}_${idCounter++}`;
    selectedFiles.push({ id, file });

    const wrap = document.createElement('div');
    wrap.className = 'thumb';
    wrap.dataset.id = id;

    const img = document.createElement('img');
    const url = URL.createObjectURL(file);
    img.onload = () => URL.revokeObjectURL(url);
    img.src = url;

    const remove = document.createElement('button');
    remove.className = 'remove';
    remove.type = 'button';
    remove.textContent = '×';
    remove.addEventListener('click', function(){
      selectedFiles = selectedFiles.filter(it => it.id !== id);
      thumbs.removeChild(wrap);
      syncInputFiles();
    });

    wrap.appendChild(img);
    wrap.appendChild(remove);
    thumbs.appendChild(wrap);
  }

  input.addEventListener('change', function(e){
    const files = Array.from(e.target.files || []);
    files.forEach(file => addFile(file));
    input.value = '';
    syncInputFiles();
  });
});

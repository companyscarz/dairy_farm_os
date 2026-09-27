function toggleSidebar(){const s=document.getElementById('sidebar');if(s)s.classList.toggle('open')}
if('serviceWorker' in navigator){window.addEventListener('load',()=>navigator.serviceWorker.register('/sw.js').catch(()=>{}))}
document.querySelectorAll('form').forEach(form=>{form.addEventListener('submit',()=>{const b=form.querySelector('button[type="submit"],button:not([type])');if(b&&b.dataset.noLoading!=='true'){b.disabled=true;setTimeout(()=>b.disabled=false,5000)}})})

const selected = document.querySelector(".selected");
const optionsContainer = document.querySelector(".options-container");
const searchBox = document.querySelector(".search-box input");

const optionsList = document.querySelectorAll(".option");

selected.addEventListener("click", () => {
  optionsContainer.classList.toggle("active");

  searchBox.value = "";
  filterList("");

  if (optionsContainer.classList.contains("active")) {
    searchBox.focus();
  }
});

optionsList.forEach(o => {
  o.addEventListener("click", () => {
    selected.innerHTML = o.querySelector("label").innerHTML;
    optionsContainer.classList.remove("active");
  });
});

var go = document.getElementById("go");
  if (go) {
    go.addEventListener("click", function (e) {
    var a=selected.innerHTML;
    if (a=='Select Player'){
        alert('Please select a player');
    }
    else{
        $.ajax({
            url: '/test',
            type: 'POST',
            data: { player: a},
            success: function(response) {
                // Handle the response from Flask
                console.log('Response:', response);
                var p=document.getElementById("player-photo")
                if (response['result']=="https://www.iplt20.com/assets/images/default-headshot.png"){
                    p.src=response['result'];
                    p.classList=[]
                    p.classList.add('icon11');
                }
                else{
                    p.src=response['result'];
                    p.classList=[]
                    p.classList.add('icon10')
                    };
                document.getElementById('batting_img').style.display='block'
                document.getElementById('bowling_img').style.display='block'
                document.getElementById('other-stats').style.display='block'
                document.getElementById('bowling').style.display='block'
                document.getElementById('fielding').style.display='block'
                document.getElementById('batting').style.display='block'
                document.getElementById('m1-box').style.display='block'
                var bl1a=document.getElementById('bl1a')
                var bl2a=document.getElementById('bl2a')
                var bl3a=document.getElementById('bl3a')
                var bl4a=document.getElementById('bl4a')
                var bl5a=document.getElementById('bl5a')
                var bl6a=document.getElementById('bl6a')
                var bl7a=document.getElementById('bl7a')
                var bol1a=document.getElementById('bol1a')
                var bol2a=document.getElementById('bol2a')
                var bol3a=document.getElementById('bol3a')
                var bol4a=document.getElementById('bol4a')
                var bol5a=document.getElementById('bol5a')
                var bol6a=document.getElementById('bol6a')
                var bol7a=document.getElementById('bol7a')
                var fl1a=document.getElementById('fl1a')
                var fl2a=document.getElementById('fl2a')
                var fl3a=document.getElementById('fl3a')
                var osl1a=document.getElementById('osl1a')
                var osl2a=document.getElementById('osl2a')
                var osl3a=document.getElementById('osl3a')
                var m2a=document.getElementById('m2a')
                bl1a.innerHTML=response['runs']
                bl2a.innerHTML=response['avg']
                bl3a.innerHTML=response['sr']
                bl4a.innerHTML=response['plus30']
                bl5a.innerHTML=response['plus100']
                bl6a.innerHTML=response['fours']
                bl7a.innerHTML=response['sixes']
                bol1a.innerHTML=response['overs']
                bol2a.innerHTML=response['wickets']
                bol3a.innerHTML=response['economy']
                bol4a.innerHTML=response['aveg']
                bol5a.innerHTML=response['srt']
                bol6a.innerHTML=response['wicket3']
                bol7a.innerHTML=response['wicket5']
                fl1a.innerHTML=response['runout']
                fl2a.innerHTML=response['stumped']
                fl3a.innerHTML=response['catch']
                osl1a.innerHTML=response['tpf'].replace(/ /g, "&nbsp;")+'&nbsp;&nbsp;&nbsp;&nbsp'
                osl2a.innerHTML=response['p1']
                osl3a.innerHTML=response['p2']
                m2a.innerHTML=response['mat_played']
                if (response['image']=='nodata'){
                    $('#bat_graph').attr('src','static/images/img/nodata.jpg');
                }
                else{
                    var imageSrc = 'data:image/png;base64,' + response['image'];
                    $('#bat_graph').attr('src',imageSrc);
                }
                if (response['image1']=='nodata'){
                    $('#bowl_graph').attr('src','static/images/img/nodata.jpg');
                }
                else{
                    var imageSrc1 = 'data:image/png;base64,' + response['image1'];
                    $('#bowl_graph').attr('src',imageSrc1);
                }

            },
        });
}
      })
      }


searchBox.addEventListener("keyup", function(e) {
  filterList(e.target.value);
});
const filterList = searchTerm => {
  searchTerm = searchTerm.toLowerCase();
  optionsList.forEach(option => {
    let label = option.firstElementChild.nextElementSibling.innerText.toLowerCase();
    if (label.indexOf(searchTerm) != -1) {
      option.style.display = "block";
    } else {
      option.style.display = "none";
    }
  });
};

const selected1 = document.querySelector(".selected1");
const optionsContainer1 = document.querySelector(".options-container1");
const searchBox1 = document.querySelector(".search-box1 input");

const optionsList1 = document.querySelectorAll(".option1");

selected1.addEventListener("click", () => {
  optionsContainer1.classList.toggle("active");

  searchBox1.value = "";
  filterList1("");

  if (optionsContainer1.classList.contains("active")) {
    searchBox1.focus();
  }
});

optionsList1.forEach(o => {
  o.addEventListener("click", () => {
    selected1.innerHTML = o.querySelector("label").innerHTML;
    console.log(selected1.innerHTML)
    optionsContainer1.classList.remove("active");
  });
});

searchBox1.addEventListener("keyup", function(e) {
  filterList1(e.target.value);
});

const filterList1 = searchTerm1 => {
  searchTerm1 = searchTerm1.toLowerCase();
  optionsList1.forEach(option => {
    let label = option.firstElementChild.nextElementSibling.innerText.toLowerCase();
    if (label.indexOf(searchTerm1) != -1) {
      option.style.display = "block";
    } else {
      option.style.display = "none";
    }
  });
};



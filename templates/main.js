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
    var t1=document.getElementById("t1");
    //t1.src=`http://127.0.0.1:5000/static/images/ipl_tlogo/${a}.svg`
    t1.src = `/static/images/ipl_tlogo/${encodeURIComponent(a)}.svg`;

    var t2=document.getElementById("t2");
    //t2.src=`http://127.0.0.1:5000/static/images/ipl_tlogo/${a}.svg`
    t2.src = `/static/images/ipl_tlogo/${encodeURIComponent(a)}.svg`;

    t1.classList=[];
    t2.classList=[];
    if (a=='Chennai Super Kings'){
        t1.classList.add('csk-1-icon');
        t2.classList.add('csk-1-ficon');

    }
    else if (a=='Gujarat Titans'){
        t1.classList.add('gt-1-icon')
        t2.classList.add('gt-1-ficon')
    }
    else if (a=='Delhi Capitals'){
        t1.classList.add('dc-1-icon')
        t2.classList.add('dc-1-ficon')
    }
    else if (a=='Rajasthan Royals'){
        t1.classList.add('rr-1-icon')
        t2.classList.add('rr-1-ficon')
    }
    else if (a=='Sunrisers Hyderabad'){
        t1.classList.add('srh-1-icon')
        t2.classList.add('srh-1-ficon')
    }
    else if (a=='Mumbai Indians'){
        t1.classList.add('mi-1-icon')
        t2.classList.add('mi-1-ficon')
    }
    else if (a=='Lucknow Super Giants'){
        t1.classList.add('lsg-1-icon')
        t2.classList.add('lsg-1-ficon')
    }
    else if (a=='Royal Challengers Bangalore'){
        t1.classList.add('rcb-1-icon')
        t2.classList.add('rcb-1-ficon')
    }
    else if (a=='Punjab Kings'){
        t1.classList.add('pbks-1-icon')
        t2.classList.add('pbks-1-ficon')
    }
    else if (a=='Kolkata Knight Riders'){
        t1.classList.add('kkr-1-icon')
        t2.classList.add('kkr-1-ficon')
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

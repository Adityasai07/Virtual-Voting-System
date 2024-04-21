let switchCtn = document.querySelector("#switch-cnt");
let switchC1 = document.querySelector("#switch-c1");
let switchC2 = document.querySelector("#switch-c2");
let switchBtn = document.querySelectorAll(".switch-btn");
let aContainer = document.querySelector("#a-container");
let bContainer = document.querySelector("#b-container");
let allButtons = document.querySelectorAll(".submit");

let getButtons = (e) => e.preventDefault()

let changeForm = (e) => {

    switchCtn.classList.add("is-gx");
    setTimeout(function(){
        switchCtn.classList.remove("is-gx");
    }, 1500)

    switchCtn.classList.toggle("is-txr");

    switchC1.classList.toggle("is-hidden");
    switchC2.classList.toggle("is-hidden");
    aContainer.classList.toggle("is-txl");
    bContainer.classList.toggle("is-txl");
    bContainer.classList.toggle("is-z200");
}

let mainF = (e) => {
    for (var i = 0; i < allButtons.length; i++)
        allButtons[i].addEventListener("click", getButtons );
    for (var i = 0; i < switchBtn.length; i++)
        switchBtn[i].addEventListener("click", changeForm)
}

window.addEventListener("load", mainF);

function validateEmailRegister(){
    let x = document.getElementById("text1").value;
    let y = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if(y.test(x)){
        document.getElementById("valid1").innerHTML = "";
    }else{
        document.getElementById("valid1").innerHTML = "Invalid Email";
    }
}

function validateEmailLogin(){
    let x = document.getElementById("text2").value;
    let y = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if(y.test(x)){
        document.getElementById("valid2").innerHTML = "";
    }else{
        document.getElementById("valid2").innerHTML = "Invalid Email";
    }
}

// function validPassword(){
//     let x = document.getElementById("password");
//     let y = document.getElementById("Cpassword");
//     if(x !== y){
//         document.getElementById("valid3").innerHTML = "Password Not Matched";
//     }else{
//         document.getElementById("valid3").innerHTML = "";
//     }
// }

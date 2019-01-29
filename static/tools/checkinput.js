function checkPhone(str) {
    const re = /^[1][3,4,5,7,8][0-9]{9}$/;
    if (re.test(str)) {
        return true;
    } else {
        return false;
    }
}

function checkEmail(str){
    const re = /^(\w-*\.*)+@(\w-?)+(\.\w{2,})+$/;
    if(re.test(str)){
        return true;
    }else{
        return false;
    }
}
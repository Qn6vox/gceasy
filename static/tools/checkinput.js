function checkPhone(str) {
    const re = /^[1][3,4,5,7,8][0-9]{9}$/;
    return !!re.test(str);
}

function checkEmail(str) {
    const re = /^(\w-*\.*)+@(\w-?)+(\.\w{2,})+$/;
    return !!re.test(str);
}
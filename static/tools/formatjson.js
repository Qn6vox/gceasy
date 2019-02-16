function formatJson(json, indent, leftBracesInSameLine){
    function getIndentStr(level){
        var str = '';
        for(var i=0; i<level; i++) str += (indent || '  ');
        return str;
    }
    function format(obj, level){
        level = level == undefined ? 0 : level;
        var result = '';
        if(typeof obj == 'object' && obj != null){
            var isArray = obj instanceof Array, idx = 0;
            result += (isArray ? '[' : '{') + '\n';
            for(var i in obj){
                result += (idx++ > 0 ? ',\n' : '');
                var nextIsObj = (typeof obj[i] == 'object' && obj[i] != null), indentStr = getIndentStr(level+1);
                result += (isArray && nextIsObj) ? '' : indentStr;
                result += isArray ? '' : ('"' + i + '": ' + (nextIsObj && !leftBracesInSameLine ? '\n' : '') );
                result += (!nextIsObj || (nextIsObj && leftBracesInSameLine && !isArray)) ? '' : indentStr;
                result += format(obj[i], level+1);
            }
            result += '\n' + getIndentStr(level) + (isArray ? ']' : '}') + '';
        }else { // 如果是 null、number、boolean、string
            var quot = typeof obj == 'string' ? '"' : '';
            result += (quot + obj + quot + '');
        }
        return result;
    }
    return format(eval('(' + json + ')'));
}
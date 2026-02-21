javascript:(function(){
    /* 1. 작동 확인용 알림 (성공하면 알림창 뜸) */
    var delCount = 0;

    /* 2. 대화상자(Dialog) 속성 가진 놈 무조건 삭제 */
    var dialogs = document.querySelectorAll('[role="dialog"]');
    dialogs.forEach(function(e){ e.remove(); delCount++; });

    /* 3. 화면 전체를 덮는 놈(투명 배경) 무조건 삭제 */
    var overlays = document.querySelectorAll('div');
    overlays.forEach(function(div){
        var style = window.getComputedStyle(div);
        if(style.position === 'fixed' && style.zIndex > 100) {
            /* 화면 가득 채운 놈이면 삭제 */
            if(div.clientWidth >= window.innerWidth && div.clientHeight >= window.innerHeight) {
                div.remove();
                delCount++;
            }
        }
    });

    /* 4. 'Sign in' 글자가 포함된 고정창 삭제 (확인사살) */
    var all = document.getElementsByTagName('*');
    for(var i=0; i<all.length; i++){
        if(all[i].innerText && all[i].innerText.includes('Sign in or sign up')) {
            var parent = all[i].closest('[style*="fixed"]');
            if(parent) { parent.remove(); delCount++; }
        }
    }

    /* 5. 스크롤 풀기 */
    document.body.style.overflow = 'auto';
    
    /* 6. 결과 알림 */
    if(delCount > 0) {
        alert("💥 펑! 로그인 창을 삭제했습니다.");
    } else {
        alert("⚠️ 이미 삭제되었거나 찾을 수 없습니다.");
    }
})();

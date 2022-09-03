var copyRandomList = function(head) {
    if(!head) return null;
    let cur = head, preHead = new Node(), temp = preHead, map = new Map();
    while(cur) {
        temp.val = cur.val;
        temp.next = cur.next ? new Node() : null;
        map.set(cur,temp);// ��temp����ֵ������
        temp = temp.next;
        cur = cur.next;
    }
    temp = preHead;
    while(head) {
        // ͨ�����õ�ַ�ҵ���Ӧ������ڵ�
        temp.random = head.random ? map.get(head.random): null;
        head = head.next;
        temp = temp.next;
    }
    return preHead;
};
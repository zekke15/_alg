# -*- coding: utf-8 -*-
"""第四週第二題：九種演算法的通用迭代框架（需 numpy）。"""
import numpy as np


def generic_iterator(transition_func, is_finished, initial_state, max_iter=1000):
    """依序更新狀態並檢查停止條件；回傳（最新狀態，迭代次數，是否正常結束）。"""
    if max_iter < 1:
        raise ValueError('max_iter 必須 >= 1')
    state = initial_state
    for iteration in range(max_iter):
        next_state = transition_func(state)
        arr = np.asarray(next_state, dtype=float)
        if not np.all(np.isfinite(arr)):
            raise ArithmeticError(f'第 {iteration + 1} 次迭代產生 NaN/Infinity')
        if is_finished(state, next_state, iteration):
            return next_state, iteration + 1, True
        state = next_state
    return state, max_iter, False


def show(name, result, iters, ok):
    print(f'\n{name}\n結果：{result}\n次數：{iters}；停止條件：{"達成" if ok else "未達成（已達次數上限）"}')


def demo_fixed_point():
    transition = lambda X: np.array([.5*X[0]-.2*X[1]+.3, .2*X[0]+.5*X[1]+.4])
    stop = lambda old,new,i: np.linalg.norm(new-old) < 1e-6
    res,n,ok=generic_iterator(transition,stop,np.array([0.,0.]))
    show('1. 二維固定點迭代',np.round(res,6),n,ok)
    return res


def demo_newton():
    def transition(x):
        if abs(2*x) < 1e-12:
            raise ZeroDivisionError('牛頓法導數接近零')
        return x-(x*x-4)/(2*x)
    stop=lambda old,new,i: abs(new*new-4)<1e-10 and abs(new-old)<1e-6
    res,n,ok=generic_iterator(transition,stop,1.0)
    show('2. 牛頓法：x²-4=0',round(res,9),n,ok)
    return res


def demo_gauss_seidel():
    A=np.array([[4.,-1.,0.],[-1.,4.,-1.],[0.,-1.,4.]])
    b=np.array([7.,2.,13.]); size=len(b)
    def transition(x):
        newer=x.copy()
        for i in range(size):
            left=np.dot(A[i,:i],newer[:i]); right=np.dot(A[i,i+1:],x[i+1:])
            newer[i]=(b[i]-left-right)/A[i,i]
        return newer
    stop=lambda old,new,i: np.max(np.abs(new-old))<1e-6 and np.linalg.norm(A@new-b)<1e-5
    res,n,ok=generic_iterator(transition,stop,np.zeros(size))
    show('3. Gauss-Seidel 解 Ax=b',np.round(res,6),n,ok)
    return res


def demo_power_iteration():
    A=np.array([[4.,1.,.5],[1.,3.,.2],[.5,.2,2.]])
    rng=np.random.default_rng(42)
    v=rng.random(3); v/=np.linalg.norm(v)
    def transition(v):
        w=A@v; norm=np.linalg.norm(w)
        if norm==0: raise ArithmeticError('矩陣乘積向量為零')
        return w/norm
    def stop(old,new,i):
        lam=float(new@A@new)
        return np.linalg.norm(A@new-lam*new)<1e-6
    res,n,ok=generic_iterator(transition,stop,v)
    lam=res@A@res
    show('4. Power Iteration 最大特徵值',round(float(lam),6),n,ok)
    return lam


def demo_qr_algorithm():
    A=np.array([[4.,1.,-2.],[1.,2.,0.],[-2.,0.,3.]])
    def transition(matrix):
        q,r=np.linalg.qr(matrix)
        return r@q
    stop=lambda old,new,i: np.linalg.norm(new-np.diag(np.diag(new)))<1e-7
    res,n,ok=generic_iterator(transition,stop,A,max_iter=3000)
    values=np.sort(np.diag(res))
    show('5. QR 演算法：特徵值（排序）',np.round(values,6),n,ok)
    return values


def demo_rk4():
    def f(t,y): return y-t+1
    h=.2; t_end=2.
    def transition(state):
        t,y=state
        dt=min(h,t_end-t)
        k1=f(t,y); k2=f(t+dt/2,y+dt*k1/2)
        k3=f(t+dt/2,y+dt*k2/2); k4=f(t+dt,y+dt*k3)
        return (t+dt,y+dt*(k1+2*k2+2*k3+k4)/6)
    stop=lambda old,new,i: new[0]>=t_end-1e-12
    res,n,ok=generic_iterator(transition,stop,(0.,1.),max_iter=20)
    show('6. RK4：到達 t=2 的固定步長積分',tuple(round(x,6) for x in res),n,ok)
    return res


def demo_pagerank():
    M=np.array([[0.,0.,1.,.5],[1/3,0.,0.,.5],[1/3,.5,0.,0.],[1/3,.5,0.,0.]])
    d=.85; size=4; G=d*M+(1-d)/size*np.ones((size,size))
    transition=lambda r:G@r
    stop=lambda old,new,i: np.linalg.norm(new-old,1)<1e-8
    res,n,ok=generic_iterator(transition,stop,np.ones(size)/size)
    show('7. PageRank',np.round(res,6),n,ok)
    return res


def demo_kmeans():
    rng=np.random.default_rng(42)
    X=np.vstack([rng.standard_normal((15,2))+np.array([2,2]),rng.standard_normal((15,2))+np.array([-2,-2])])
    centroids=X[[0,15]].copy() # 從兩群各選一點，避免初始兩中心在同一群
    def transition(centroids):
        distances=np.linalg.norm(X[:,None,:]-centroids[None,:,:],axis=2)
        labels=np.argmin(distances,axis=1)
        return np.array([X[labels==j].mean(axis=0) if np.any(labels==j) else centroids[j] for j in range(2)])
    stop=lambda old,new,i: np.max(np.abs(new-old))<1e-6
    res,n,ok=generic_iterator(transition,stop,centroids)
    show('8. K-Means 分群中心',np.round(res,5),n,ok)
    return res


def demo_em_two_coin():
    trials=np.array([[5,5],[9,1],[8,2],[4,6],[7,3]])
    def transition(theta):
        a,b=theta
        counts=np.zeros(4)
        for heads,tails in trials:
            pa=a**heads*(1-a)**tails
            pb=b**heads*(1-b)**tails
            wa=pa/(pa+pb) if pa+pb>0 else .5
            wb=1-wa
            counts+=np.array([wa*heads,wa*tails,wb*heads,wb*tails])
        ah,at,bh,bt=counts
        return (ah/(ah+at),bh/(bh+bt))
    stop=lambda old,new,i: max(abs(new[0]-old[0]),abs(new[1]-old[1]))<1e-6
    res,n,ok=generic_iterator(transition,stop,(.6,.5))
    show('9. EM：兩枚硬幣的正面機率',tuple(round(x,6) for x in res),n,ok)
    return res


def main():
    print('第四週習題：通用迭代框架與九種應用')
    for func in (demo_fixed_point,demo_newton,demo_gauss_seidel,demo_power_iteration,demo_qr_algorithm,demo_rk4,demo_pagerank,demo_kmeans,demo_em_two_coin):
        func()

if __name__=='__main__':
    main()

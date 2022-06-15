import random
import queue
import matplotlib.pyplot as plt

def test(choice):
    
    reference_string = []
    dirty_bit = []
    
    if choice=="Random":
        while len( reference_string ) <= 200000 :
           start=random.randint(1,800)
           extend=random.randint(1,25)
           if (start + extend) <= 800 :
               for i in range(extend) :
                   reference_string.append(start + i) 
                   dirty_bit.append(random.randint(0,1))
        
            
    elif choice=="Locality":
        while len( reference_string ) <= 200000 :
            start=random.randint(1,800)
            between=random.uniform(1/25,1/15)
            extend=int(800*between)
            half=int(extend/2)
            if 0 <= (start + half) <= 800 :
                for i in range (half)  :
                    reference_string.append(start + i)
                    if (start - (i+1))>=0 :
                        reference_string.append(start - (i+1))
                        
                    dirty_bit.append(random.randint(0,1))
                    
     
                    
    elif choice=="My_ref":
        while len( reference_string ) <= 200000 :
            start=random.randint(1,800)
            between=random.uniform(1/25,1/15)
            extend=int(800*between)
            if 0 <= (start + extend) <= 800 :
                for i in range (extend)  :
                    reference_string.append(start + i)
                    dirty_bit.append(random.randint(0,1))
            
                for j in range (8000-extend)  :
                    reference_string.append(random.randint(start,start + i) )
                    dirty_bit.append(random.randint(0,1))
            
            
    
    return reference_string,dirty_bit

def FIFO (frames,reference_string,dirty_bit):   #當dirty_bit = 1 (被修改過)時，disk_IO額外計算一次
    
    pagefault_list = []
    interrupt_list = []
    disk_IO_list = []
    
    for num in frames:
       
       q = queue.Queue(num)
       
       page_fault = 0
       interrupt = 0      #每次存取queue時，就是一次interrupt
       disk_IO = 0
       
       for ref in reference_string:
           
           if q.empty():
               q.put(ref)
               page_fault = page_fault + 1
               interrupt = interrupt + 2
               disk_IO = disk_IO + 1
               
           else:
               
               if ref in q.queue:
                   page_fault = page_fault
                   interrupt = interrupt + 1
                   
               else:
                   
                   if q.full():                   
                       victim = q.get()       #OS select a victim page,change該bit值,若值為0則無須swap out
                       
                       if ( dirty_bit[reference_string.index( victim )] == 1 ) :  #有修改過，多加一次disk_IO
                           interrupt = interrupt + 1
                           disk_IO = disk_IO + 1
                       
                       page_fault = page_fault +1
                       interrupt = interrupt + 2
                       disk_IO = disk_IO + 1
                       q.put(ref)
                
                   else:
                       q.put(ref)
                       page_fault = page_fault + 1
                       interrupt = interrupt + 2
                       disk_IO = disk_IO + 1
                       
       pagefault_list.append(page_fault)
       interrupt_list.append(interrupt)
       disk_IO_list.append(disk_IO)            
       
    print(pagefault_list)
    print(interrupt_list)
    print(disk_IO_list)

    return pagefault_list,interrupt_list,disk_IO_list    

def ARB (frames,reference_string,dirty_bit):   #以FIFO為基礎,以<reference bit,dirty_bit>配對值,為挑選victim page之依據
    
    page_table = []       
    reference_table = {}
    pagefault_list = []
    interrupt_list = []
    disk_IO_list = []
    
    
    for num in frames:
        
        page_fault = 0
        interrupt = 0      #每次修改refence_bit和 dirty_bit時，計算一次interrupt
        disk_IO = 0
        count=0
       
        for ref in reference_string:
            
           
           
            if len(page_table)<num:                 #當page table還沒滿時
               
                if ref in page_table :                               #已在page table內,被reference過
                    page_fault = page_fault
                    interrupt = interrupt + 1
                    if reference_table[ref] < 128:     #把現有的reference string的bit變新的
                        reference_table[ref]+=128
                        
                    interrupt= interrupt + 1
                   
                 
                else:                                               #沒在page table內,沒被reference
                   
                    page_table.append(ref)
                    reference_table[ref]=128             #加入reference string,bit最高位加1,因設refer bit,所以 intrrupt多+1
                    page_fault = page_fault + 1
                    interrupt = interrupt + 3
                    disk_IO = disk_IO + 1
                    
                                      
                       
                                       
                   
            else:                                    #page table滿了
                if ref in page_table :                               #已在page table內,被reference過
                    page_fault = page_fault
                    interrupt= interrupt + 1
                    if reference_table[ref]<128:       #把現有的reference string的bit變新的
                        reference_table[ref]+=128
                        
                    interrupt = interrupt + 1
                   
                               
                else:
                   
                    t=256

                    for key in reference_table.keys():    #依reference bit大小決定丟出去的string
                        if reference_table[key] < t:
                            victim = key
                            t=reference_table[key]
                    interrupt = interrupt + 1

                    if (dirty_bit[reference_string.index(victim)])==1 :
                        interrupt = interrupt + 1
                        disk_IO = disk_IO + 1

                    page_table.remove(victim)
                    page_table.append(ref)
                    reference_table.pop(victim)
                    reference_table[ref]=128
                    page_fault = page_fault + 1
                    interrupt = interrupt + 3
                    disk_IO = disk_IO + 1 
                       
            count += 1
            
            if count == 8 :                         #週期到，reference bit往後一位
                for k in reference_table.keys():
                    reference_table[k]/=2
                    
                count = 0
                interrupt = interrupt + 1
                
            
            
        pagefault_list.append(page_fault)
        interrupt_list.append(interrupt)
        disk_IO_list.append(disk_IO)            
       
    print(pagefault_list)
    print(interrupt_list)
    print(disk_IO_list)

    return pagefault_list,interrupt_list,disk_IO_list


def ESC (frames,reference_string,dirty_bit):   #以FIFO為基礎,以<reference bit,dirty_bit>配對值,為挑選victim page之依據
    
    page_table = []
    ESC_table = []
    pagefault_list = []
    interrupt_list = []
    disk_IO_list = []
    
    
    for num in frames:
        
       page_fault = 0
       interrupt = 0      #每次修改refence_bit和 dirty_bit時，計算一次interrupt
       disk_IO = 0
       
       for ref in reference_string:
           
           if len(page_table)<num:                 #當page table還沒滿時
               
               if ref in page_table :                               #已在page table內,被reference過
                   page_fault = page_fault
                   interrupt = interrupt + 1
                   
                   if dirty_bit[ref] == 1 :
                       ESC_table[page_table.index(ref)] = [ 1 , 1 ]
                       interrupt = interrupt + 2
                       disk_IO = disk_IO + 1
                       
                   else:
                       ESC_table[page_table.index(ref)] = [ 1 , 0 ]
                       interrupt = interrupt + 1
                                              
               else:                                               #沒在page table內,沒被reference
                   
                   page_table.append(ref)
                   page_fault = page_fault + 1
                   interrupt = interrupt + 2
                   disk_IO = disk_IO + 1
                                      
                   if dirty_bit[ref] == 1 :
                       ESC_table.append([ 0 , 1 ])
                       disk_IO = disk_IO + 1                     
                       
                   else:
                       ESC_table.append([ 0 , 0 ])
                       
                   
                   
           else:                                    #page table滿了
               if ref in page_table :                               #已在page table內,被reference過
                   page_fault = page_fault
                   interrupt = interrupt + 1
                   
                   if dirty_bit[ref] == 1 :
                       ESC_table[page_table.index(ref)] = [ 1 , 1 ]
                       interrupt = interrupt + 2
                       disk_IO = disk_IO + 1
                       
                   else:
                       ESC_table[page_table.index(ref)] = [ 1 , 0 ]
                       interrupt = interrupt + 1
           
               else:
                   interrupt = interrupt + 1
                   #對<R,M>值根據大小做變動
                   if [ 0 , 0 ] in ESC_table :
                       page_table.remove(page_table[ESC_table.index([ 0 , 0 ])])
                       page_table.append(ref)
                       page_fault = page_fault + 1
                       disk_IO = disk_IO + 1
                                                                     
                   elif [ 0 , 1 ] in ESC_table :
                       page_table.remove(page_table[ESC_table.index([ 0 , 1 ])])
                       page_table.append(ref)
                       page_fault = page_fault + 1
                       interrupt = interrupt + 1
                       disk_IO = disk_IO + 2
                       
                       
                   elif [ 1 , 0 ] in ESC_table :
                       page_table.remove(page_table[ESC_table.index([ 1 , 0 ])])
                       page_table.append(ref)
                       page_fault = page_fault + 1
                       interrupt = interrupt + 1
                       disk_IO = disk_IO + 1
                                                                     
                   elif [ 1 , 1 ] in ESC_table :
                       page_table.remove(page_table[ESC_table.index([ 1 , 1 ])])
                       page_table.append(ref)
                       page_fault = page_fault + 1
                       interrupt = interrupt + 2
                       disk_IO = disk_IO + 2
                       
                                            
       pagefault_list.append(page_fault)
       interrupt_list.append(interrupt)
       disk_IO_list.append(disk_IO)            
       
    print(pagefault_list)
    print(interrupt_list)
    print(disk_IO_list)

    return pagefault_list,interrupt_list,disk_IO_list
    

def MyAlgo (frames,reference_string,dirty_bit) :  #以FIFO為基礎,以<reference bit,dirty_bit>配對值,為挑選victim page之依據
    
    page_table = []
    pagefault_list = []
    interrupt_list = []
    disk_IO_list = []
    
    
    for num in frames:
        
       page_fault = 0
       interrupt = 0      #每次修改refence_bit和 dirty_bit時，計算一次interrupt
       disk_IO = 0
       index = 0
       
       for ref in reference_string:
           
           if len(page_table)<num:                 #當page table還沒滿時
               
               if ref in page_table :                               #已在page table內,被reference過
                   page_fault = page_fault
                   interrupt = interrupt + 1
                   
               else:
                   page_table.append(ref)
                   page_fault = page_fault + 1
                   interrupt = interrupt + 2
                   disk_IO = disk_IO + 1
                                              
          
                   
                   
           else:                                    #page table滿了
               if ref in page_table :                               #已在page table內,被reference過
                   page_fault = page_fault
                   interrupt = interrupt + 1
                   
                          
               else:
                   
                    #Knuth's multiplicative
                    hash_key = ref * 2654435761 % num

                    page_table[hash_key] = ref  

                    #有修改過，因此需寫回disk，多加一次diskIO
                    if ( dirty_bit[reference_string.index( ref )] == 1 ) :
                        interrupt = interrupt + 1
                        disk_IO = disk_IO + 1

                    page_fault = page_fault + 1
                    interrupt = interrupt + 2
                    disk_IO = disk_IO + 1
                       
           index = index + 1  
                                 
       pagefault_list.append(page_fault)
       interrupt_list.append(interrupt)
       disk_IO_list.append(disk_IO)            
       
    print(pagefault_list)
    print(interrupt_list)
    print(disk_IO_list)

    return pagefault_list,interrupt_list,disk_IO_list






if __name__ == '__main__' :
    
    frames=[20, 40, 60, 80, 100]
    
    #Random
    reference_string,dirty_bit=test("Random")
    FIFO_pagefault_list,FIFO_interrupt_list,FIFO_disk_IO_list=FIFO (frames,reference_string,dirty_bit)
    ARB_pagefault_list,ARB_interrupt_list,ARB_disk_IO_list=ARB (frames,reference_string,dirty_bit)
    ESC_pagefault_list,ESC_interrupt_list,ESC_disk_IO_list=ESC (frames,reference_string,dirty_bit)
    MyAlgo_pagefault_list,MyAlgo_interrupt_list,MyAlgo_disk_IO_list=MyAlgo (frames,reference_string,dirty_bit)
    
    
    #page fault
    plt.figure()
    plt.title("Page fault of Random Reference Strings")
    plt.xlabel("frames") # 標示x軸
    plt.ylabel("page fault")# 標示y軸
    
    plt.plot(frames,FIFO_pagefault_list,label='FIFO', linestyle = "--")
    plt.plot(frames,ARB_pagefault_list,label='ARB')
    plt.plot(frames,ESC_pagefault_list,label='ESC')
    plt.plot(frames,MyAlgo_pagefault_list,label='MyAlgo')
    plt.legend(loc='upper right')
    plt.savefig("Page fault of Random Reference Strings")
    plt.show()
    
    #interrupt
    plt.figure()
    plt.title("Interrupt of Random Reference Strings")
    plt.xlabel("frames") # 標示x軸
    plt.ylabel("Interrupt")# 標示y軸
    
    plt.plot(frames,FIFO_interrupt_list,label='FIFO', linestyle = "--")
    plt.plot(frames,ARB_interrupt_list,label='ARB')
    plt.plot(frames,ESC_interrupt_list,label='ESC')
    plt.plot(frames,MyAlgo_interrupt_list,label='MyAlgo')
    plt.legend(loc='upper right')
    plt.savefig("Interrupt of Random Reference Strings")
    plt.show()
                
    #disk IO
    plt.figure()
    plt.title("Disk I/O of Random Reference Strings")
    plt.xlabel("frames") # 標示x軸
    plt.ylabel("Disk I/O")# 標示y軸
    
    plt.plot(frames,FIFO_disk_IO_list,label='FIFO', linestyle = "--")
    plt.plot(frames,ARB_disk_IO_list,label='ARB')
    plt.plot(frames,ESC_disk_IO_list,label='ESC')
    plt.plot(frames,MyAlgo_disk_IO_list,label='MyAlgo')
    plt.legend(loc='upper right')
    plt.savefig("Disk IO of Random Reference Strings")
    plt.show()                          
           
       
           
    #Locality           
    reference_string,dirty_bit=test("Locality")
    FIFO_pagefault_list,FIFO_interrupt_list,FIFO_disk_IO_list=FIFO (frames,reference_string,dirty_bit)
    ARB_pagefault_list,ARB_interrupt_list,ARB_disk_IO_list=ARB (frames,reference_string,dirty_bit)
    ESC_pagefault_list,ESC_interrupt_list,ESC_disk_IO_list=ESC (frames,reference_string,dirty_bit)
    MyAlgo_pagefault_list,MyAlgo_interrupt_list,MyAlgo_disk_IO_list=MyAlgo (frames,reference_string,dirty_bit)
    
    
    #page fault
    plt.figure()
    plt.title("Page fault of Locality Reference Strings")
    plt.xlabel("frames") # 標示x軸
    plt.ylabel("page fault")# 標示y軸
    
    plt.plot(frames,FIFO_pagefault_list,label='FIFO', linestyle = "--")
    plt.plot(frames,ARB_pagefault_list,label='ARB')
    plt.plot(frames,ESC_pagefault_list,label='ESC')
    plt.plot(frames,MyAlgo_pagefault_list,label='MyAlgo')
    plt.legend(loc='upper right')
    plt.savefig("Page fault of Locality Reference Strings")
    plt.show()
    
    #interrupt
    plt.figure()
    plt.title("Interrupt of Locality Reference Strings")
    plt.xlabel("frames") # 標示x軸
    plt.ylabel("Interrupt")# 標示y軸
    
    plt.plot(frames,FIFO_interrupt_list,label='FIFO', linestyle = "--")
    plt.plot(frames,ARB_interrupt_list,label='ARB')
    plt.plot(frames,ESC_interrupt_list,label='ESC')
    plt.plot(frames,MyAlgo_interrupt_list,label='MyAlgo')
    plt.legend(loc='upper right')
    plt.savefig("Interrupt of Locality Reference Strings")
    plt.show()
                
    #disk IO
    plt.figure()
    plt.title("Disk I/O of Locality Reference Strings")
    plt.xlabel("frames") # 標示x軸
    plt.ylabel("Disk I/O")# 標示y軸
    
    plt.plot(frames,FIFO_disk_IO_list,label='FIFO', linestyle = "--")
    plt.plot(frames,ARB_disk_IO_list,label='ARB')
    plt.plot(frames,ESC_disk_IO_list,label='ESC')
    plt.plot(frames,MyAlgo_disk_IO_list,label='MyAlgo')
    plt.legend(loc='upper right')
    plt.savefig("Disk IO of Locality Reference Strings")
    plt.show()
    
    
    
    #My_ref           
    reference_string,dirty_bit=test("My_ref")
    FIFO_pagefault_list,FIFO_interrupt_list,FIFO_disk_IO_list=FIFO (frames,reference_string,dirty_bit)
    ARB_pagefault_list,ARB_interrupt_list,ARB_disk_IO_list=ARB (frames,reference_string,dirty_bit)
    ESC_pagefault_list,ESC_interrupt_list,ESC_disk_IO_list=ESC (frames,reference_string,dirty_bit)
    MyAlgo_pagefault_list,MyAlgo_interrupt_list,MyAlgo_disk_IO_list=MyAlgo (frames,reference_string,dirty_bit)
    
    
    #page fault
    plt.figure()
    plt.title("Page fault of My Reference Strings")
    plt.xlabel("frames") # 標示x軸
    plt.ylabel("page fault")# 標示y軸
    
    plt.plot(frames,FIFO_pagefault_list,label='FIFO', linestyle = "--")
    plt.plot(frames,ARB_pagefault_list,label='ARB')
    plt.plot(frames,ESC_pagefault_list,label='ESC')
    plt.plot(frames,MyAlgo_pagefault_list,label='MyAlgo')
    plt.legend(loc='upper right')
    plt.savefig("Page fault of My Reference Strings")
    plt.show()
    
    #interrupt
    plt.figure()
    plt.title("Interrupt of My Reference Strings")
    plt.xlabel("frames") # 標示x軸
    plt.ylabel("Interrupt")# 標示y軸
    
    plt.plot(frames,FIFO_interrupt_list,label='FIFO', linestyle = "--")
    plt.plot(frames,ARB_interrupt_list,label='ARB')
    plt.plot(frames,ESC_interrupt_list,label='ESC')
    plt.plot(frames,MyAlgo_interrupt_list,label='MyAlgo')
    plt.legend(loc='upper right')
    plt.savefig("Interrupt of My Reference Strings")
    plt.show()
                
    #disk IO
    plt.figure()
    plt.title("Disk I/O of My Reference Strings")
    plt.xlabel("frames") # 標示x軸
    plt.ylabel("Disk I/O")# 標示y軸
    
    plt.plot(frames,FIFO_disk_IO_list,label='FIFO', linestyle = "--")
    plt.plot(frames,ARB_disk_IO_list,label='ARB')
    plt.plot(frames,ESC_disk_IO_list,label='ESC')
    plt.plot(frames,MyAlgo_disk_IO_list,label='MyAlgo')
    plt.legend(loc='upper right')
    plt.savefig("Disk IO of My Reference Strings")
    plt.show()

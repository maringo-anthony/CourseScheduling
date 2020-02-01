// I worked with 
//ams9qx@virginia.edu
//jmt5rg@virginia.edu
//fm4cg@virginia.edu
void fibarray(unsigned char *dest, unsigned num){
    
    if(num == 1){
        dest[0]=1;
    }
    if(num >=2){
        dest[0]=1;
        dest[1]=1;
    }

    for(int i = 2; i < (int)num; i ++){

        dest[i] = dest[i-1]+dest[i-2];
    }
}

unsigned long nextprime(unsigned long x){
    for(unsigned long i =(x+1);i==i;i++){
        if(isprime(i) == 1)
            return i;
    }
}

int isprime(unsigned long x){
    if (x == 0){ // might not need this idk
      return 0;
    }
    if (x <=1){
        return 1;
    }
    for(unsigned long i = 2; i<x; i++){
        if(x % i ==0)
            return 0;
    }
    return 1;
}


int nondup(int *arr, unsigned length){
	int count = 0;
	for(int i=0; i<length;i++){
		count = 0;
		for(int j=0;j<length;j++){
			if(*(arr+j) == *(arr+i)){
				count++;
			}
		}
		if(count == 1)
			return *(arr+i);
	}

}

void reverse(int *arr, unsigned length){

	int newArr[length];
	int pos = 0;

	for(int i = length-1;i>=0;i--){
		newArr[pos] = *(arr+i);
		pos+=1;
	}

	for(int i = 0; i<length;i++){
		*(arr+i) = newArr[i];
	}
}

void capitalize(char *s){ // this one works 


	// capital letters between ranges 65(A) and 90(Z)
	// lowercase letters between ranges 97(a) and 122(Z)

    while(*s != '\0'){
        if(*s>=97 && *s<=122){ 
            *s = (*s)-32;
        } 
        s+=1;
    }
}

long recpow(long x, unsigned char e){
	if(e!=0){
		return(x*recpow(x,e-1));
	}
	return 1;
}
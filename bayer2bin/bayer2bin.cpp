#include <stdint.h>
#include <fstream>

int main(int argc, char** argv)
{
	uint32_t arr[64] = {
	 0, 32, 8, 40, 2, 34, 10, 42, /* 8x8 Bayer ordered dithering */
	48, 16, 56, 24, 50, 18, 58, 26, /* pattern. Each input pixel */
	12, 44, 4, 36, 14, 46, 6, 38, /* is scaled to the 0..63 range */
	60, 28, 52, 20, 62, 30, 54, 22, /* before looking in this table */
	 3, 35, 11, 43, 1, 33, 9, 41, /* to determine the action. */
	51, 19, 59, 27, 49, 17, 57, 25,
	15, 47, 7, 39, 13, 45, 5, 37,
	63, 31, 55, 23, 61, 29, 53, 21 };
	
	std::ofstream f;
	f.open("bayer.raw", std::ofstream::binary);
	
	for (int idx = 0; idx < 64; ++idx)
	{
		f.write((const char*)&arr[idx], sizeof(uint32_t));
	}
	
	f.close();
	
	return 0;
}

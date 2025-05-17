// rastertozj.c — ESC/POS filter with secure signal handling & error checks

#include <cups/cups.h>
#include <cups/ppd.h>
#include <cups/raster.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <fcntl.h>
#include <signal.h>
#include <unistd.h>

#define DEBUGFILE "/tmp/debugraster.txt"
struct settings_ {
  int cashDrawer1, cashDrawer2, blankSpace, feedDist, cutting;
} settings;

struct command { int length; const unsigned char *data; };
static const unsigned char init_cmd[]       = {0x1B,0x40};
static const unsigned char cut_cmd[]        = {0x1D,0x56,0x01};
static const unsigned char raster_cmd[]     = {0x1D,0x76,0x30,0x00};
static const unsigned char drawer1_cmd[]    = {0x1B,0x70,0x00,0x19,0xFA};
static const unsigned char drawer2_cmd[]    = {0x1B,0x70,0x01,0x19,0xFA};
static const struct command printerInit     = {2, init_cmd};
static const struct command fullCut         = {3, cut_cmd};
static const struct command rasterStart     = {4, raster_cmd};
static const struct command drawerCmds[2]  = { {5, drawer1_cmd}, {5, drawer2_cmd} };

#ifdef DEBUGP
static FILE *lfd = NULL;
#endif

// Secure signal handling
static volatile sig_atomic_t cancel_flag = 0;
static void handle_signal(int sig) { cancel_flag = 1; }
static void setup_signals(void) {
  struct sigaction sa; memset(&sa,0,sizeof(sa));
  sa.sa_handler = handle_signal; sa.sa_flags = SA_RESTART;
  sigemptyset(&sa.sa_mask);
  sigaction(SIGTERM,&sa,NULL);
  sigaction(SIGINT, &sa,NULL);
  sigaction(SIGPIPE,&sa,NULL);
}

// Safe output
static void safe_putchar(unsigned char c) {
  if (putchar(c)==EOF) { perror("write"); exit(1); }
}
static void output_bytes(const unsigned char *d,int n){for(int i=0;i<n;i++)safe_putchar(d[i]);}

// PPD option helper
static int get_ppd_choice(const char *name, ppd_file_t *ppd) {
  ppd_option_t *opt=ppdFindOption(ppd,name);
  if(!opt) return 0;
  ppd_choice_t *ch=ppdFindMarkedChoice(ppd,name);
  if(!ch) ch=ppdFindChoice(opt,opt->defchoice);
  return ch?atoi(ch->choice):0;
}

static void initializeSettings(const char *opts) {
  const char *ppd_path = getenv("PPD");
  if(!ppd_path||strncmp(ppd_path,"/etc/cups/ppd/",13)){fprintf(stderr,"Invalid PPD\n");exit(1);}
  ppd_file_t *ppd=ppdOpenFile(ppd_path);
  if(!ppd){perror("ppdOpen");exit(1);}
  ppdMarkDefaults(ppd);
  cups_option_t *a; int n=cupsParseOptions(opts,0,&a);
  if(n>0){cupsMarkOptions(ppd,n,a);cupsFreeOptions(n,a);}
  settings.cashDrawer1 = get_ppd_choice("CashDrawer1Setting",ppd);
  settings.cashDrawer2 = get_ppd_choice("CashDrawer2Setting",ppd);
  settings.blankSpace  = get_ppd_choice("BlankSpace",ppd);
  settings.feedDist    = get_ppd_choice("FeedDist",ppd);
  settings.cutting     = get_ppd_choice("Cutting",ppd);
  ppdClose(ppd);
}

static void jobSetup(void) {
  if(settings.cashDrawer1==1) output_bytes(drawerCmds[0].data,5);
  if(settings.cashDrawer2==1) output_bytes(drawerCmds[1].data,5);
  output_bytes(printerInit.data,2);
}

static void pageEnd(void) {
  for(int i=0;i<settings.feedDist;i++){safe_putchar(0x1B);safe_putchar(0x4A);safe_putchar(24);}
  if(settings.cutting==1) output_bytes(fullCut.data,3);
}

static void jobShutdown(void) {
  if(settings.cutting==2) output_bytes(fullCut.data,3);
  if(settings.cashDrawer1==2) output_bytes(drawerCmds[0].data,5);
  if(settings.cashDrawer2==2) output_bytes(drawerCmds[1].data,5);
  output_bytes(printerInit.data,2);
}

int main(int argc,char *argv[]) {
  if(argc<6||argc>7){fprintf(stderr,"Usage: rastertozj job user title copies opts [file]\n");return 1;}
  setup_signals();
  initializeSettings(argv[5]);

  int fd=0;
  if(argc==7 && strcmp(argv[6],"-")!=0){
    if(strncmp(argv[6],"/var/spool/cups/",16)){fprintf(stderr,"Bad file %s\n",argv[6]);return 1;}
    fd=open(argv[6],O_RDONLY); if(fd<0){perror("open");return 1;}
  }

#ifdef DEBUGP
  lfd=fopen(DEBUGFILE,"w");
#endif

  jobSetup();
  cups_raster_t *ras=cupsRasterOpen(fd,CUPS_RASTER_READ);
  if(!ras){perror("cupsRasterOpen");return 1;}

  cups_page_header2_t hdr;
  unsigned char *stripe=NULL;
  size_t stripe_size=0;
  int page=0;

  while(!cancel_flag && cupsRasterReadHeader2(ras,&hdr)) {
    if(hdr.cupsHeight<=0||hdr.cupsBytesPerLine<=0) break;
    if(!stripe) {
      size_t sz=hdr.cupsBytesPerLine*24;
      if(hdr.cupsBytesPerLine>65536/24||sz>65536){fprintf(stderr,"Stripe too big\n");break;}
      stripe=malloc(sz); if(!stripe){perror("malloc");break;} stripe_size=sz;
    }
    page++;
    for(int y=0;y<hdr.cupsHeight && !cancel_flag;){
      int chunk=(hdr.cupsHeight-y>24?24:hdr.cupsHeight-y);
      size_t bytes=((size_t)chunk*hdr.cupsBytesPerLine+7)&~7;
      if(bytes>stripe_size){fprintf(stderr,"Overflow\n");break;}
      unsigned char *p=stripe;
      int i;
      for(i=0;i<chunk && cupsRasterReadPixels(ras,p,hdr.cupsBytesPerLine);i++) p+=bytes;
      y+=i;
      size_t j; for(j=0;j<bytes && stripe[j]==0;j++);
      if(j<bytes){
        output_bytes(rasterStart.data,4);
        safe_putchar((unsigned char)(hdr.cupsWidth&0xFF));
        safe_putchar((unsigned char)(hdr.cupsWidth>>8));
        safe_putchar((unsigned char)(chunk&0xFF));
        safe_putchar((unsigned char)(chunk>>8));
        fwrite(stripe,1,i*bytes,stdout);
        safe_putchar(0x1B); safe_putchar(0x4A); safe_putchar(0);
      }
    }
    pageEnd();
  }

  jobShutdown();
  if(stripe) free(stripe);
  cupsRasterClose(ras);
  if(fd) close(fd);
  return (page>0 && !cancel_flag)?0:1;
}
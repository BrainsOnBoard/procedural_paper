d= readtable('scaling_data.csv');

baseclr= [
          0.258 0.448 0.71
          0.918 0.498 0.272
          0.183 0.67 0.38
          0.826 0.263 0.305 ];

alpha= [ 0.1 0.5 1.0 ];

% extract raw data from table
rd= d{:,:};
rd= rd(1:2:end,:);

figure;
get(gca,'position')
hold on;
for i=1:4  % bar groups (different rows)
  for j= 1:4 % different hw
    for k= 1:3 % different algorithm
      x= 16*(i-1)+3.5*(j-1)+k;
      xid= (j-1)*3+k+2;
      yid= i;
      fc= baseclr(j,:);
      fa= alpha(k);
      bar(x,rd(yid,xid), 'facecolor',fc, 'facealpha', fa);
    end
  end
end
set(gca,'yscale','log');
ylim([ 0.1 2*10^4 ]);
set(gca,'ytick', 10.^(0:4));
set(gca,'yticklabel', []);
xlim([ -1 65 ]);
xlabel('Number of neurons');
xt= ((0:3)+0.5)*16;
set(gca,'xtick', xt);
set(gca,'xticklabel',{'10^3','10^4','10^5','10^6'});
set(gca,'ygrid','on');
set(gca,'yminorgrid','off');
set(gca,'linewidth',1);
set(gca,'gridcolor', [ 0.6 0.6 0.6 ]);
%set(gca,'xcolor', [ 0.6 0.6 0.6 ]);
%set(gca,'ycolor', [ 0.6 0.6 0.6 ]);
set(gca,'ticklength', [ 0 0 ]);

% let's make a legend
axes('position', [ 0.15 0.6 0.5 0.5 ]);
hold on;
lbl= {'Procedural', 'Bitmask', 'Sparse'};
for i=1:3
  y= (i-1)*1.8;
  fc= alpha(i)*[ 0.95 0.95 0.95 ];
  r=rectangle('position', [ 0 y 2 1 ], 'facecolor', fc,'linewidth',1);
  text(2.4, y + 0.5, lbl{i},'fontsize',12);
end
ylim([ 0 7 ]);
xlim([ 0 15 ]);
set(gca,'visible', 'off');

set(gcf,'paperposition', [ 0 0 6 2 ]);
print('-r300','-dpng', 'bars.png');
